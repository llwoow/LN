"""LN original one-joint command-contract simulator; never opens a robot device.

All times in the API are host-local monotonic milliseconds supplied by the caller.
This is an executable protocol lesson, not a hard-real-time motor controller.
"""
from dataclasses import dataclass, field
import json
import math


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


@dataclass
class Guard:
    session: str = 'ln-lesson'
    max_age_ms: float = 120.0
    max_angle_rad: float = 1.0
    max_speed_rad_s: float = 0.6
    observations: dict = field(default_factory=dict)
    state: str = 'DISARMED'
    seq: int = -1
    reference_rad: float = 0.0
    target_rad: float = 0.0
    speed_rad_s: float = 0.0
    expires_ms: float = -1.0
    previous_tick_ms: float | None = None

    def observe(self, observation_id, capture_ms):
        if not isinstance(observation_id, str) or not observation_id or not number(capture_ms):
            raise ValueError('Invalid local observation')
        if observation_id in self.observations:
            raise ValueError('Observation identity cannot be reassigned')
        self.observations[observation_id] = capture_ms

    def arm(self):
        self.state = 'HOLD'

    def disarm(self):
        self.state = 'DISARMED'
        self.speed_rad_s = 0.0
        self.expires_ms = -1.0

    def accept(self, payload, now_ms):
        if self.state == 'DISARMED':
            return 'disarmed'
        if not number(now_ms):
            return 'bad_local_clock'
        try:
            if len(payload) > 1024:
                return 'oversize'
            p = json.loads(payload, parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
        except (TypeError, ValueError, json.JSONDecodeError):
            return 'malformed'
        required = {'version', 'session', 'seq', 'observation_id', 'target_rad', 'vmax_rad_s'}
        if not isinstance(p, dict) or set(p) != required:
            return 'schema'
        if type(p['version']) is not int or p['version'] != 1 or p['session'] != self.session:
            return 'identity'
        if type(p['seq']) is not int or not 0 <= p['seq'] < 2**63 or p['seq'] <= self.seq:
            return 'out_of_order'
        if not isinstance(p['observation_id'], str) or p['observation_id'] not in self.observations:
            return 'unknown_observation'
        age = now_ms - self.observations[p['observation_id']]
        if age < 0 or age > self.max_age_ms:
            return 'stale_or_future'
        target, speed = p['target_rad'], p['vmax_rad_s']
        if not number(target) or not number(speed):
            return 'nonfinite_or_type'
        if abs(target) > self.max_angle_rad or not 0 < speed <= self.max_speed_rad_s:
            return 'outside_limits'
        self.seq = p['seq']
        self.target_rad, self.speed_rad_s = float(target), float(speed)
        self.expires_ms = self.observations[p['observation_id']] + self.max_age_ms
        self.state = 'RUN'
        return 'accepted'

    def tick(self, now_ms):
        if not number(now_ms):
            raise ValueError('Local clock must be finite')
        if self.previous_tick_ms is None:
            dt = 0.0
        else:
            dt = (now_ms - self.previous_tick_ms) / 1000.0
            if dt < 0:
                raise ValueError('Local monotonic time moved backwards')
        self.previous_tick_ms = now_ms
        if self.state == 'RUN' and now_ms > self.expires_ms:
            self.state = 'HOLD'
        if self.state == 'RUN':
            delta = self.target_rad - self.reference_rad
            limit = self.speed_rad_s * dt
            self.reference_rad += max(-limit, min(delta, limit))
        return self.reference_rad


def packet(seq, observation_id='obs-0', target_rad=.5, vmax_rad_s=.4, **overrides):
    p = {'version': 1, 'session': 'ln-lesson', 'seq': seq,
         'observation_id': observation_id, 'target_rad': target_rad, 'vmax_rad_s': vmax_rad_s}
    p.update(overrides)
    return json.dumps(p, allow_nan=False)
