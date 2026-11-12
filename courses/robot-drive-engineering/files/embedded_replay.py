"""LN original offline command receiver model; never opens a device or drives a motor.

Wire format uses 8-bit octets, little endian. This is a teaching UART format,
not CANopen, CiA 402, EtherCAT or a production motor-control protocol.
"""
from dataclasses import dataclass
import struct
import json

MASK32 = (1 << 32) - 1
FRAME = struct.Struct('<2sBBHhHHH')


def crc16(data):
    """Polynomial 0x1021, init FFFF, no reflection, xorout 0."""
    crc = 0xFFFF
    for octet in data:
        crc ^= octet << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def encode(seq, angle_mrad=300, speed_mrad_s=500, lease_ms=100, version=1, kind=0x10):
    raw = FRAME.pack(b'\xa5\x5a', version, kind, seq, angle_mrad, speed_mrad_s, lease_ms, 0)
    return raw[:-2] + struct.pack('<H', crc16(raw[2:-2]))


@dataclass
class Receiver:
    state: str = 'DISARMED'
    last_seq: int | None = None
    received_ms: int | None = None
    lease_ms: int = 0
    accepted: int = 0
    target: tuple | None = None

    def arm(self):
        # This asserts only a simulated permit; real interlocks are not modeled.
        if self.state != 'DISARMED':
            return False
        self.state = 'READY'
        self.last_seq = None
        self.received_ms = None
        return True

    def receive(self, raw, now_ms):
        if len(raw) != FRAME.size:
            return 'length'
        sof, version, kind, seq, angle, speed, lease, check = FRAME.unpack(raw)
        if sof != b'\xa5\x5a' or version != 1 or kind != 0x10:
            return 'format'
        if crc16(raw[2:-2]) != check:
            return 'crc'
        if self.state not in ('READY', 'ACTIVE'):
            return 'not-ready'
        if not (-1000 <= angle <= 1000 and 0 < speed <= 1000 and 10 <= lease <= 200):
            return 'range'
        if self.last_seq is not None:
            delta = (seq - self.last_seq) & 0xFFFF
            if not (0 < delta < 0x8000):
                return 'sequence'
        # Publish the whole validated record together in the model.
        self.target = (angle, speed)
        self.last_seq = seq
        self.received_ms = now_ms & MASK32
        self.lease_ms = lease
        self.accepted += 1
        self.state = 'ACTIVE'
        return 'accepted'

    def tick(self, now_ms):
        if self.state == 'ACTIVE':
            age = ((now_ms & MASK32) - self.received_ms) & MASK32
            if age > self.lease_ms:
                # Request stopping; no physical braking or power-stage action is simulated.
                self.state = 'STOP_REQUESTED'
                self.target = None
        return self.state


class Framer:
    """Bounded fixed-length example; loses malformed sync candidates then resynchronizes."""
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, block):
        frames = []
        for octet in block:
            self.buffer.append(octet)
            while len(self.buffer) >= 2 and self.buffer[:2] != b'\xa5\x5a':
                del self.buffer[0]
            if len(self.buffer) == FRAME.size:
                candidate = bytes(self.buffer)
                if crc16(candidate[2:-2]) == int.from_bytes(candidate[-2:], 'little'):
                    frames.append(candidate)
                    self.buffer.clear()
                else:
                    del self.buffer[0]
        return frames


def self_check():
    assert FRAME.size == 14
    assert crc16(b'123456789') == 0x29B1
    r = Receiver()
    assert r.receive(encode(1), 0) == 'not-ready'
    assert r.arm()
    assert r.receive(encode(65535), 0xFFFFFFFC) == 'accepted'
    assert r.receive(encode(0), 1) == 'accepted'  # sequence wraps forward
    assert r.receive(encode(0), 2) == 'sequence'
    assert r.receive(encode(65534), 3) == 'sequence'
    assert r.receive(encode(1, angle_mrad=1100), 4) == 'range'
    broken = bytearray(encode(1)); broken[6] ^= 1
    assert r.receive(broken, 5) == 'crc'
    assert r.tick(101) == 'ACTIVE'  # age == 100, inclusive lease boundary
    assert r.tick(102) == 'STOP_REQUESTED'
    assert r.receive(encode(1), 103) == 'not-ready'  # stale state cannot self-rearm
    q = Receiver(); q.arm(); assert q.receive(encode(10, lease_ms=10), 0xFFFFFFFC) == 'accepted'
    assert q.tick(5) == 'ACTIVE'  # uint32 age == 9 across timer wrap
    assert q.tick(7) == 'STOP_REQUESTED'
    f = Framer()
    wire = b'noise' + encode(20) + bytes(broken) + encode(21)
    decoded = []
    for byte in wire:
        decoded.extend(f.feed(bytes([byte])))
        assert len(f.buffer) <= 13
    assert decoded == [encode(20), encode(21)]
    deadline_us = 50 - (25 + 2 + 3 + 12 + 1 + 2)
    assert deadline_us == 5
    report = dict(frame_octets=FRAME.size, uart_115200_ms=FRAME.size*10/115200*1000,
                  crc_check='29B1', deadline_margin_us=deadline_us,
                  parser_frames=len(decoded), final_state=r.state,
                  scope='host-side original model; no UART/CAN adapter, DSP, motor or physical stop has been exercised')
    return report


if __name__ == '__main__':
    print(json.dumps(self_check(), ensure_ascii=False, indent=2))
