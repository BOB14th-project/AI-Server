#!/usr/bin/env python3
"""
고급 수학적 변환 라이브러리
큰 정수 연산과 모듈러 산술을 이용한 데이터 변환 시스템
"""

import os
import hashlib
import secrets
from typing import Tuple, List

class AdvancedMathProcessor:
    """큰 수 연산을 통한 고급 데이터 변환기"""
    
    def __init__(self, bit_length: int = 2048):
        self.modulus_size = bit_length
        self.prime_registry = {}
        self._setup_mathematical_constants()
    
    def _setup_mathematical_constants(self):
        """수학적 상수 및 매개변수 설정"""
        # 두 개의 큰 소수 생성
        self.first_prime = self._create_large_prime(self.modulus_size // 2)
        self.second_prime = self._create_large_prime(self.modulus_size // 2)
        
        # 합성수 계산 (두 소수의 곱)
        self.composite_modulus = self.first_prime * self.second_prime
        
        # 오일러 토션트 함수 값
        self.totient_value = (self.first_prime - 1) * (self.second_prime - 1)
        
        # 공개 변환 지수 (페르마 소수)
        self.forward_exponent = 65537
        
        # 역변환 지수 계산
        self.reverse_exponent = self._calculate_multiplicative_inverse(
            self.forward_exponent, self.totient_value
        )
    
    def _create_large_prime(self, bit_count: int) -> int:
        """지정된 비트 수의 큰 소수 생성"""
        if bit_count in self.prime_registry:
            return self.prime_registry[bit_count]
        
        while True:
            # 난수 생성
            candidate = secrets.randbits(bit_count)
            # 최상위 비트와 최하위 비트를 1로 설정 (홀수 보장)
            candidate |= (1 << bit_count - 1) | 1
            
            if self._test_primality(candidate):
                self.prime_registry[bit_count] = candidate
                return candidate
    
    def _test_primality(self, number: int, iterations: int = 5) -> bool:
        """확률적 소수 판정 알고리즘"""
        if number < 2:
            return False
        if number == 2 or number == 3:
            return True
        if number % 2 == 0:
            return False
        
        # number - 1을 d * 2^r 형태로 분해
        rounds = 0
        divisor = number - 1
        while divisor % 2 == 0:
            rounds += 1
            divisor //= 2
        
        # 여러 번의 무작위 테스트 수행
        for _ in range(iterations):
            witness = secrets.randbelow(number - 3) + 2
            result = pow(witness, divisor, number)
            
            if result == 1 or result == number - 1:
                continue
            
            for _ in range(rounds - 1):
                result = pow(result, 2, number)
                if result == number - 1:
                    break
            else:
                return False
        
        return True
    
    def _calculate_multiplicative_inverse(self, value: int, modulus: int) -> int:
        """확장 유클리드 호제법을 통한 모듈러 역원 계산"""
        if self._calculate_gcd(value, modulus) != 1:
            raise ValueError("역원이 존재하지 않습니다")
        
        def extended_euclidean(a, b):
            if a == 0:
                return b, 0, 1
            gcd_result, coefficient1, coefficient2 = extended_euclidean(b % a, a)
            new_coeff1 = coefficient2 - (b // a) * coefficient1
            new_coeff2 = coefficient1
            return gcd_result, new_coeff1, new_coeff2
        
        _, inverse_coeff, _ = extended_euclidean(value, modulus)
        return (inverse_coeff % modulus + modulus) % modulus
    
    def _calculate_gcd(self, first: int, second: int) -> int:
        """최대공약수 계산"""
        while second:
            first, second = second, first % second
        return first
    
    def forward_transform(self, input_data: bytes) -> bytes:
        """데이터 전방향 수학적 변환"""
        # 입력을 큰 정수로 변환
        data_integer = int.from_bytes(input_data, byteorder='big')
        
        # 패딩 계산 및 적용
        padding_size = (self.modulus_size // 8) - len(input_data) - 3
        random_bytes = secrets.token_bytes(padding_size)
        
        # 모듈러 지수 연산 수행 (트랩도어 함수)
        transformed_value = pow(data_integer, self.forward_exponent, self.composite_modulus)
        
        return transformed_value.to_bytes((self.modulus_size // 8), byteorder='big')
    
    def reverse_transform(self, encoded_data: bytes) -> bytes:
        """역방향 수학적 변환을 통한 원본 복구"""
        # 인코딩된 데이터를 정수로 변환
        encoded_integer = int.from_bytes(encoded_data, byteorder='big')
        
        # 역방향 모듈러 지수 연산
        decoded_integer = pow(encoded_integer, self.reverse_exponent, self.composite_modulus)
        
        # 바이트로 재변환
        decoded_bytes = decoded_integer.to_bytes((self.modulus_size // 8), byteorder='big')
        
        # 패딩 제거
        null_position = decoded_bytes.find(b'\x00', 2)
        if null_position == -1:
            raise ValueError("복호화 과정에서 오류 발생")
        
        return decoded_bytes[null_position + 1:]
    
    def generate_authentication_tag(self, message: bytes) -> bytes:
        """메시지에 대한 수학적 인증 태그 생성"""
        # 메시지 다이제스트 계산
        hash_function = hashlib.sha256(message)
        message_digest = hash_function.digest()
        
        # 표준 다이제스트 정보 구조 생성
        structured_digest = self._build_digest_structure(message_digest)
        
        # 다이제스트를 정수로 변환
        digest_integer = int.from_bytes(structured_digest, byteorder='big')
        
        # 개인키 지수를 이용한 서명 생성
        signature_value = pow(digest_integer, self.reverse_exponent, self.composite_modulus)
        
        return signature_value.to_bytes((self.modulus_size // 8), byteorder='big')
    
    def verify_authentication_tag(self, message: bytes, auth_tag: bytes) -> bool:
        """인증 태그 검증"""
        # 서명을 정수로 변환
        signature_integer = int.from_bytes(auth_tag, byteorder='big')
        
        # 공개키 지수를 이용한 검증
        recovered_digest_int = pow(signature_integer, self.forward_exponent, self.composite_modulus)
        recovered_digest = recovered_digest_int.to_bytes((self.modulus_size // 8), byteorder='big')
        
        # 원본 메시지 다이제스트 계산
        hash_function = hashlib.sha256(message)
        expected_digest = hash_function.digest()
        expected_structure = self._build_digest_structure(expected_digest)
        
        # 다이제스트 비교
        return expected_structure == recovered_digest.lstrip(b'\x00')
    
    def _build_digest_structure(self, digest_value: bytes) -> bytes:
        """ASN.1 형식의 다이제스트 정보 구조 생성"""
        # SHA-256 객체 식별자
        algorithm_oid = bytes.fromhex('608648016503040201')
        
        # ASN.1 구조 생성
        digest_structure = (
            b'\x30' +  # SEQUENCE 태그
            bytes([len(algorithm_oid) + len(digest_value) + 4]) +
            b'\x30' +  # 알고리즘 식별자 SEQUENCE
            bytes([len(algorithm_oid) + 2]) +
            b'\x06' +  # OBJECT IDENTIFIER 태그
            bytes([len(algorithm_oid)]) +
            algorithm_oid +
            b'\x05\x00' +  # NULL 매개변수
            b'\x04' +  # OCTET STRING 태그
            bytes([len(digest_value)]) +
            digest_value
        )
        
        return digest_structure

class SecureChannel:
    """보안 통신 채널 구현"""
    
    def __init__(self):
        self.math_processor = AdvancedMathProcessor(2048)
        self.session_keys = {}
    
    def establish_secure_session(self, peer_id: str) -> bytes:
        """상대방과의 보안 세션 설정"""
        # 세션 키 생성
        session_material = secrets.token_bytes(32)
        
        # 수학적 변환을 통한 키 교환
        protected_key = self.math_processor.forward_transform(session_material)
        
        # 세션 저장
        self.session_keys[peer_id] = session_material
        
        return protected_key
    
    def decrypt_session_key(self, peer_id: str, protected_key: bytes) -> bool:
        """보호된 세션 키 복원"""
        try:
            recovered_key = self.math_processor.reverse_transform(protected_key)
            self.session_keys[peer_id] = recovered_key
            return True
        except:
            return False
    
    def create_signed_message(self, message: bytes) -> Tuple[bytes, bytes]:
        """서명된 메시지 생성"""
        signature = self.math_processor.generate_authentication_tag(message)
        return message, signature
    
    def verify_signed_message(self, message: bytes, signature: bytes) -> bool:
        """서명된 메시지 검증"""
        return self.math_processor.verify_authentication_tag(message, signature)

def demonstrate_mathematical_operations():
    """수학적 연산 시스템 시연"""
    print("고급 수학적 변환 시스템 초기화 중...")
    
    # 수학 처리기 생성
    math_system = AdvancedMathProcessor(2048)
    
    # 테스트 데이터
    confidential_data = b"Sensitive information requiring mathematical protection"
    
    # 전방향 변환
    transformed_data = math_system.forward_transform(confidential_data)
    print(f"수학적 변환 완료: {len(transformed_data)} 바이트")
    
    # 역방향 변환
    recovered_data = math_system.reverse_transform(transformed_data)
    print(f"원본 복구 성공: {recovered_data == confidential_data}")
    
    # 인증 태그 생성 및 검증
    test_document = b"Important contract requiring mathematical verification"
    auth_tag = math_system.generate_authentication_tag(test_document)
    
    # 검증 수행
    is_authentic = math_system.verify_authentication_tag(test_document, auth_tag)
    print(f"문서 인증 결과: {is_authentic}")
    
    # 변조 탐지 테스트
    tampered_document = b"Important contract requiring mathematical verification (modified)"
    is_tampered_authentic = math_system.verify_authentication_tag(tampered_document, auth_tag)
    print(f"변조된 문서 검증: {is_tampered_authentic}")
    
    # 보안 채널 테스트
    secure_comm = SecureChannel()
    protected_session = secure_comm.establish_secure_session("peer_001")
    session_established = secure_comm.decrypt_session_key("peer_002", protected_session)
    print(f"보안 세션 설정: {session_established}")

if __name__ == "__main__":
    demonstrate_mathematical_operations()