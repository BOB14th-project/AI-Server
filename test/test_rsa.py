#!/usr/bin/env python3
"""
테스트용 RSA 암호화를 사용하는 Python 파일
PQC Inspector가 이 파일에서 비양자내성암호 사용을 탐지해야 함
"""

import rsa
from cryptography.hazmat.primitives.asymmetric import rsa as crypto_rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import hashlib

def generate_rsa_keypair():
    """RSA 키 쌍 생성"""
    (public_key, private_key) = rsa.newkeys(2048)
    return public_key, private_key

def rsa_encrypt_message(message, public_key):
    """RSA로 메시지 암호화"""
    encrypted = rsa.encrypt(message.encode('utf-8'), public_key)
    return encrypted

def rsa_decrypt_message(encrypted_message, private_key):
    """RSA로 메시지 복호화"""
    decrypted = rsa.decrypt(encrypted_message, private_key)
    return decrypted.decode('utf-8')

def create_rsa_signature(message, private_key):
    """RSA 디지털 서명 생성"""
    signature = rsa.sign(message.encode('utf-8'), private_key, 'SHA-256')
    return signature

def verify_rsa_signature(message, signature, public_key):
    """RSA 디지털 서명 검증"""
    try:
        rsa.verify(message.encode('utf-8'), signature, public_key)
        return True
    except rsa.VerificationError:
        return False

# Cryptography 라이브러리 사용 예제
def advanced_rsa_example():
    """고급 RSA 사용 예제"""
    # RSA 키 생성
    private_key = crypto_rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    
    # 메시지 서명
    message = b"Important message"
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    return signature

if __name__ == "__main__":
    print("RSA 암호화 테스트 시작...")
    
    # RSA 키 생성
    pub_key, priv_key = generate_rsa_keypair()
    
    # 메시지 암호화/복호화
    original_message = "This is a secret message"
    encrypted = rsa_encrypt_message(original_message, pub_key)
    decrypted = rsa_decrypt_message(encrypted, priv_key)
    
    print(f"Original: {original_message}")
    print(f"Decrypted: {decrypted}")
    
    # 디지털 서명
    signature = create_rsa_signature(original_message, priv_key)
    is_valid = verify_rsa_signature(original_message, signature, pub_key)
    print(f"Signature valid: {is_valid}")
    
    print("RSA 테스트 완료")