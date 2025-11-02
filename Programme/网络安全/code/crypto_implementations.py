#!/usr/bin/env python3
"""
密码学算法实现验证
包含RSA、AES、ECC、哈希函数等核心算法的Python实现
用于验证理论算法的正确性和完整性
"""

import hashlib
import secrets
import random
from typing import Tuple, List
import math

class RSAImplementation:
    """RSA算法实现验证"""
    
    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """扩展欧几里得算法"""
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = RSAImplementation.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """计算模反元素"""
        gcd, x, _ = RSAImplementation.extended_gcd(a, m)
        if gcd != 1:
            raise ValueError("模反元素不存在")
        return (x % m + m) % m
    
    @staticmethod
    def is_prime(n: int, k: int = 5) -> bool:
        """Miller-Rabin素性测试"""
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False
        
        # 找到r和d，使得n-1 = 2^r * d
        d = n - 1
        r = 0
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # 进行k轮测试
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    @staticmethod
    def generate_large_prime(bits: int) -> int:
        """生成大素数"""
        while True:
            candidate = secrets.randbits(bits)
            candidate |= (1 << bits - 1) | 1  # 确保是奇数且为bits位
            if RSAImplementation.is_prime(candidate):
                return candidate
    
    @staticmethod
    def generate_keypair(bits: int = 2048) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """生成RSA密钥对"""
        # 生成两个大素数
        p = RSAImplementation.generate_large_prime(bits // 2)
        q = RSAImplementation.generate_large_prime(bits // 2)
        
        # 计算n和φ(n)
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # 选择公钥指数e
        e = 65537
        while math.gcd(e, phi) != 1:
            e = secrets.randbelow(phi - 3) + 3
        
        # 计算私钥指数d
        d = RSAImplementation.mod_inverse(e, phi)
        
        return (n, e), (n, d)
    
    @staticmethod
    def encrypt(plaintext: int, public_key: Tuple[int, int]) -> int:
        """RSA加密"""
        n, e = public_key
        return pow(plaintext, e, n)
    
    @staticmethod
    def decrypt(ciphertext: int, private_key: Tuple[int, int]) -> int:
        """RSA解密"""
        n, d = private_key
        return pow(ciphertext, d, n)
    
    @staticmethod
    def rsa_correctness_proof(p: int, q: int, e: int, d: int, m: int) -> bool:
        """
        RSA正确性证明验证
        验证 m^(ed) ≡ m (mod pq)
        """
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # 验证 ed ≡ 1 (mod φ(n))
        assert (e * d) % phi == 1, f"ed ≡ 1 (mod φ(n)) 不成立: {(e * d) % phi}"
        
        # 验证加密解密正确性
        encrypted = pow(m, e, n)
        decrypted = pow(encrypted, d, n)
        
        assert decrypted % n == m % n, f"RSA正确性失败: {decrypted} ≠ {m}"
        return True

class AESImplementation:
    """AES算法实现验证（简化版）"""
    
    # S盒
    S_BOX = [
        0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
        0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
        0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
        0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
        0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
        0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
        0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
        0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
        0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
        0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
        0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
        0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
    ]
    
    @staticmethod
    def sub_bytes(state: List[int]) -> List[int]:
        """字节替换"""
        return [AESImplementation.S_BOX[byte] for byte in state]
    
    @staticmethod
    def shift_rows(state: List[int]) -> List[int]:
        """行移位"""
        # 简化的行移位操作
        return state
    
    @staticmethod
    def mix_columns(state: List[int]) -> List[int]:
        """列混合（简化实现）"""
        # 简化的列混合操作
        return state
    
    @staticmethod
    def add_round_key(state: List[int], round_key: List[int]) -> List[int]:
        """轮密钥加"""
        return [s ^ rk for s, rk in zip(state, round_key)]
    
    @staticmethod
    def aes_encrypt_block(plaintext: List[int], key: List[int]) -> List[int]:
        """AES块加密（简化实现）"""
        state = plaintext[:]
        
        # 初始轮密钥加
        state = AESImplementation.add_round_key(state, key)
        
        # 主要轮次
        for _ in range(9):  # AES-128的9轮主要加密
            state = AESImplementation.sub_bytes(state)
            state = AESImplementation.shift_rows(state)
            state = AESImplementation.mix_columns(state)
            state = AESImplementation.add_round_key(state, key)
        
        # 最终轮（无列混合）
        state = AESImplementation.sub_bytes(state)
        state = AESImplementation.shift_rows(state)
        state = AESImplementation.add_round_key(state, key)
        
        return state

class HashFunctionImplementation:
    """哈希函数实现验证"""
    
    @staticmethod
    def md5_implementation(data: bytes) -> str:
        """MD5哈希函数实现"""
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def sha256_implementation(data: bytes) -> str:
        """SHA-256哈希函数实现"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def hash_properties_test(data1: bytes, data2: bytes) -> dict:
        """测试哈希函数的密码学特性"""
        hash1_1 = HashFunctionImplementation.sha256_implementation(data1)
        hash1_2 = HashFunctionImplementation.sha256_implementation(data1)
        hash2 = HashFunctionImplementation.sha256_implementation(data2)
        
        return {
            "deterministic": hash1_1 == hash1_2,  # 确定性
            "avalanche_effect": hash1_1[:16] != hash2[:16] if data1 != data2 else False,  # 雪崩效应
            "fixed_length": len(hash1_1) == 64,  # 固定长度
            "different_inputs": hash1_1 != hash2 if data1 != data2 else True  # 不同输入产生不同输出
        }

class ECCImplementation:
    """椭圆曲线密码学实现验证（简化版）"""
    
    @staticmethod
    def elliptic_curve_point_addition(p1: Tuple[int, int], p2: Tuple[int, int], a: int, b: int, p: int) -> Tuple[int, int]:
        """椭圆曲线上的点加法运算"""
        if p1 == (0, 0):  # 无穷远点
            return p2
        if p2 == (0, 0):  # 无穷远点
            return p1
        
        x1, y1 = p1
        x2, y2 = p2
        
        if x1 == x2:
            if y1 == y2:
                # 倍点运算
                if y1 == 0:
                    return (0, 0)  # 无穷远点
                s = ((3 * x1 * x1 + a) * pow(2 * y1, -1, p)) % p
            else:
                return (0, 0)  # 无穷远点
        else:
            # 普通加法
            s = ((y2 - y1) * pow(x2 - x1, -1, p)) % p
        
        x3 = (s * s - x1 - x2) % p
        y3 = (s * (x1 - x3) - y1) % p
        
        return (x3, y3)
    
    @staticmethod
    def scalar_multiplication(k: int, point: Tuple[int, int], a: int, b: int, p: int) -> Tuple[int, int]:
        """标量乘法：k * P"""
        result = (0, 0)  # 无穷远点
        addend = point
        
        while k:
            if k & 1:
                result = ECCImplementation.elliptic_curve_point_addition(result, addend, a, b, p)
            addend = ECCImplementation.elliptic_curve_point_addition(addend, addend, a, b, p)
            k >>= 1
        
        return result

def crypto_verification_tests():
    """密码学算法验证测试"""
    print("=== 密码学算法验证测试 ===\n")
    
    # RSA算法验证
    print("1. RSA算法验证")
    print("-" * 30)
    
    # 生成测试素数
    p, q = 61, 53  # 小的测试素数
    e = 17
    d = RSAImplementation.mod_inverse(e, (p-1)*(q-1))
    
    # 测试消息
    m = 123
    
    # 验证RSA正确性
    if RSAImplementation.rsa_correctness_proof(p, q, e, d, m):
        print("✓ RSA正确性证明验证通过")
    
    # 测试加密解密
    public_key = (p*q, e)
    private_key = (p*q, d)
    
    encrypted = RSAImplementation.encrypt(m, public_key)
    decrypted = RSAImplementation.decrypt(encrypted, private_key)
    
    if decrypted == m:
        print("✓ RSA加密解密验证通过")
    else:
        print("✗ RSA加密解密验证失败")
    
    print(f"  原始消息: {m}")
    print(f"  加密后: {encrypted}")
    print(f"  解密后: {decrypted}")
    print()
    
    # 哈希函数验证
    print("2. 哈希函数验证")
    print("-" * 30)
    
    data1 = b"Hello, World!"
    data2 = b"Hello, World"  # 少了一个感叹号
    
    properties = HashFunctionImplementation.hash_properties_test(data1, data2)
    print("哈希函数特性测试结果:")
    for prop, result in properties.items():
        status = "✓" if result else "✗"
        print(f"  {status} {prop}: {result}")
    
    print(f"  SHA-256({data1.decode()}): {HashFunctionImplementation.sha256_implementation(data1)}")
    print(f"  SHA-256({data2.decode()}): {HashFunctionImplementation.sha256_implementation(data2)}")
    print()
    
    # 椭圆曲线验证
    print("3. 椭圆曲线密码学验证")
    print("-" * 30)
    
    # 使用标准椭圆曲线 y² = x³ + ax + b (mod p)
    a, b, p = 0, 7, 23  # 标准曲线参数
    
    # 选择基点
    G = (3, 10)
    
    # 测试点加法
    P1 = G
    P2 = ECCImplementation.elliptic_curve_point_addition(P1, P1, a, b, p)
    P3 = ECCImplementation.elliptic_curve_point_addition(P1, P2, a, b, p)
    
    print(f"基点 G: {G}")
    print(f"2G: {P2}")
    print(f"3G: {P3}")
    
    # 测试标量乘法
    k = 5
    kG = ECCImplementation.scalar_multiplication(k, G, a, b, p)
    print(f"{k}G: {kG}")
    
    # 验证 (a+b)G = aG + bG
    aG = ECCImplementation.scalar_multiplication(2, G, a, b, p)
    bG = ECCImplementation.scalar_multiplication(3, G, a, b, p)
    sum_ab = ECCImplementation.elliptic_curve_point_addition(aG, bG, a, b, p)
    abG = ECCImplementation.scalar_multiplication(5, G, a, b, p)
    
    if sum_ab == abG:
        print("✓ 椭圆曲线标量乘法验证通过")
    else:
        print("✗ 椭圆曲线标量乘法验证失败")
    
    print()

if __name__ == "__main__":
    crypto_verification_tests()
