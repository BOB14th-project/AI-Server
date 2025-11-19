# File: pqc_inspector_server/services/binary_preprocessor.py
# 🔧 바이너리 파일을 LLM이 분석하기 쉬운 형태로 전처리하는 모듈

import capstone
import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class BinaryPreprocessor:
    """
    바이너리 파일을 디스어셈블하고 암호화 관련 의심스러운 부분만 추출합니다.

    목표:
    1. 바이너리 → 어셈블리 변환 (Capstone)
    2. 암호화 관련 패턴 필터링
    3. LLM 컨텍스트 크기에 맞게 축약
    4. 가독성 높은 포맷으로 변환
    """

    # 암호화 관련 키워드 (대소문자 무시)
    CRYPTO_KEYWORDS = [
        # 암호화 알고리즘
        'rsa', 'aes', 'des', 'ecdsa', 'dsa', 'sha', 'md5',
        'kyber', 'dilithium', 'ntru', 'falcon', 'sphincs',
        'chacha', 'poly1305', 'gcm', 'cbc', 'ecb',

        # 암호화 관련 함수/라이브러리
        'encrypt', 'decrypt', 'cipher', 'crypto', 'ssl', 'tls',
        'openssl', 'libcrypto', 'cryptopp', 'botan',
        'key', 'priv', 'pub', 'cert', 'sign', 'verify',

        # 수학/암호 연산
        'modexp', 'modmul', 'gcd', 'inverse', 'prime',
        'rand', 'random', 'entropy', 'nonce',

        # 해시 관련
        'hash', 'digest', 'hmac', 'kdf', 'pbkdf'
    ]

    # OpenSSL 함수 패턴 (더 정확한 탐지)
    OPENSSL_FUNCTIONS = [
        'RSA_new', 'RSA_generate_key', 'RSA_public_encrypt', 'RSA_private_decrypt',
        'EVP_PKEY_new', 'EVP_PKEY_keygen', 'EVP_EncryptInit', 'EVP_DecryptInit',
        'ECDSA_sign', 'ECDSA_verify', 'EC_KEY_new', 'EC_KEY_generate_key',
        'AES_set_encrypt_key', 'AES_encrypt', 'AES_decrypt',
        'SHA256_Init', 'SHA256_Update', 'SHA256_Final'
    ]

    def __init__(self, max_context_chars: int = 15000):
        """
        Args:
            max_context_chars: LLM에 전달할 최대 문자 수 (기본 15,000자)
        """
        self.max_context_chars = max_context_chars
        print(f"   🔧 BinaryPreprocessor 초기화 (최대 컨텍스트: {max_context_chars} chars)")

    def preprocess(self, binary_data: bytes, filename: str = "binary") -> str:
        """
        바이너리 데이터를 전처리하여 LLM 분석용 텍스트로 변환

        Args:
            binary_data: 원본 바이너리 데이터
            filename: 파일명 (아키텍처 추론용)

        Returns:
            LLM이 분석할 포맷된 텍스트
        """
        print(f"   📦 바이너리 전처리 시작: {filename} ({len(binary_data)} bytes)")

        # 1. 바이너리에서 문자열 추출
        strings = self._extract_strings(binary_data)
        print(f"   📝 추출된 문자열: {len(strings)}개")

        # 2. 암호화 관련 문자열 필터링
        crypto_strings = self._filter_crypto_strings(strings)
        print(f"   🔍 암호화 관련 문자열: {len(crypto_strings)}개")

        # 3. 바이너리 → 어셈블리 디스어셈블
        disasm_blocks = self._disassemble_binary(binary_data, filename)
        print(f"   ⚙️ 디스어셈블된 블록: {len(disasm_blocks)}개")

        # 4. LLM 친화적 포맷으로 변환
        formatted_output = self._format_for_llm(
            filename=filename,
            binary_size=len(binary_data),
            crypto_strings=crypto_strings,
            disasm_blocks=disasm_blocks
        )

        print(f"   ✅ 전처리 완료: {len(formatted_output)} chars")
        return formatted_output

    def _extract_strings(self, binary_data: bytes, min_length: int = 4) -> List[str]:
        """바이너리에서 ASCII 문자열 추출"""
        # ASCII 출력 가능 문자 + 공백
        ascii_pattern = rb'[ -~]{' + str(min_length).encode() + rb',}'
        matches = re.findall(ascii_pattern, binary_data)
        return [m.decode('ascii', errors='ignore') for m in matches]

    def _filter_crypto_strings(self, strings: List[str]) -> List[Dict[str, any]]:
        """암호화 관련 문자열만 필터링"""
        crypto_strings = []

        for s in strings:
            s_lower = s.lower()

            # 키워드 매칭
            matched_keywords = [kw for kw in self.CRYPTO_KEYWORDS if kw in s_lower]

            # OpenSSL 함수 매칭
            matched_functions = [fn for fn in self.OPENSSL_FUNCTIONS if fn in s]

            if matched_keywords or matched_functions:
                crypto_strings.append({
                    'string': s,
                    'keywords': matched_keywords,
                    'functions': matched_functions,
                    'confidence': len(matched_keywords) + len(matched_functions) * 2
                })

        # 신뢰도 순으로 정렬
        crypto_strings.sort(key=lambda x: x['confidence'], reverse=True)
        return crypto_strings

    def _disassemble_binary(self, binary_data: bytes, filename: str) -> List[Dict]:
        """바이너리를 디스어셈블하고 의심스러운 블록만 추출"""

        # 아키텍처 추론 (파일명이나 매직 바이트 기반)
        arch, mode = self._detect_architecture(binary_data, filename)

        try:
            md = capstone.Cs(arch, mode)
            md.detail = True  # 상세 정보 활성화
        except capstone.CsError as e:
            print(f"   ⚠️ Capstone 초기화 실패: {e}")
            return []

        # 디스어셈블 시도
        suspicious_blocks = []
        try:
            instructions = list(md.disasm(binary_data, 0x1000))
            print(f"   🔍 총 {len(instructions)}개 instruction 디스어셈블됨")

            # 암호화 관련 instruction 탐지
            for i, insn in enumerate(instructions):
                if self._is_crypto_related_instruction(insn):
                    # 전후 컨텍스트 포함 (±15 instructions)
                    context_start = max(0, i - 15)
                    context_end = min(len(instructions), i + 15)
                    context = instructions[context_start:context_end]

                    suspicious_blocks.append({
                        'trigger_address': hex(insn.address),
                        'trigger_instruction': f"{insn.mnemonic} {insn.op_str}",
                        'context': self._format_instruction_block(context),
                        'confidence': self._calculate_confidence(insn)
                    })

        except capstone.CsError as e:
            print(f"   ⚠️ 디스어셈블 실패: {e}")

        # 중복 제거 및 신뢰도 순 정렬
        suspicious_blocks = self._deduplicate_blocks(suspicious_blocks)
        suspicious_blocks.sort(key=lambda x: x['confidence'], reverse=True)

        return suspicious_blocks

    def _detect_architecture(self, binary_data: bytes, filename: str) -> Tuple[int, int]:
        """바이너리의 아키텍처를 추론"""

        # ELF 매직 바이트 체크
        if binary_data[:4] == b'\x7fELF':
            # ELF 헤더의 5번째 바이트가 클래스 (1=32bit, 2=64bit)
            if len(binary_data) > 4:
                if binary_data[4] == 1:
                    return capstone.CS_ARCH_X86, capstone.CS_MODE_32
                elif binary_data[4] == 2:
                    return capstone.CS_ARCH_X86, capstone.CS_MODE_64

        # PE 매직 바이트 체크 (Windows)
        if binary_data[:2] == b'MZ':
            # 대부분 64비트로 가정
            return capstone.CS_ARCH_X86, capstone.CS_MODE_64

        # Mach-O 매직 바이트 체크 (macOS)
        if binary_data[:4] in [b'\xfe\xed\xfa\xce', b'\xfe\xed\xfa\xcf',
                                b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe']:
            return capstone.CS_ARCH_X86, capstone.CS_MODE_64

        # 기본값: x86-64
        print(f"   ℹ️ 알 수 없는 포맷, x86-64로 가정")
        return capstone.CS_ARCH_X86, capstone.CS_MODE_64

    def _is_crypto_related_instruction(self, insn) -> bool:
        """instruction이 암호화와 관련이 있는지 판단"""

        # mnemonic과 operand를 합쳐서 검사
        full_text = f"{insn.mnemonic} {insn.op_str}".lower()

        # 키워드 매칭
        for keyword in self.CRYPTO_KEYWORDS:
            if keyword in full_text:
                return True

        # 특정 instruction 패턴 (큰 수 연산 등)
        # RSA 등에서 사용되는 큰 정수 연산 탐지
        if insn.mnemonic in ['mul', 'imul', 'div', 'idiv', 'shl', 'shr']:
            # operand에 큰 상수가 있으면 암호화 관련일 가능성
            if any(c.isdigit() for c in insn.op_str):
                try:
                    # 16진수나 10진수 큰 값 체크
                    nums = re.findall(r'0x[0-9a-fA-F]+|\d+', insn.op_str)
                    for num in nums:
                        val = int(num, 0)
                        if val > 0x1000:  # 4096보다 큰 수
                            return True
                except:
                    pass

        # AES-NI 등 하드웨어 암호화 instruction
        if insn.mnemonic.startswith('aes') or insn.mnemonic.startswith('pclmul'):
            return True

        return False

    def _calculate_confidence(self, insn) -> float:
        """instruction의 암호화 관련성 신뢰도 계산 (0.0 ~ 1.0)"""
        confidence = 0.3  # 기본값

        full_text = f"{insn.mnemonic} {insn.op_str}".lower()

        # 키워드 매칭 점수
        matched_keywords = sum(1 for kw in self.CRYPTO_KEYWORDS if kw in full_text)
        confidence += matched_keywords * 0.15

        # AES-NI 같은 하드웨어 암호화는 확신도 높음
        if insn.mnemonic.startswith('aes'):
            confidence = 0.95

        # 함수 호출인 경우 더 높은 점수
        if insn.mnemonic in ['call', 'jmp']:
            confidence += 0.2

        return min(confidence, 1.0)

    def _format_instruction_block(self, instructions: List) -> str:
        """instruction 블록을 가독성 높게 포맷팅"""
        lines = []
        for insn in instructions:
            # 주소, mnemonic, operands를 정렬해서 표시
            lines.append(f"  {insn.address:#010x}:  {insn.mnemonic:8s} {insn.op_str}")
        return '\n'.join(lines)

    def _deduplicate_blocks(self, blocks: List[Dict]) -> List[Dict]:
        """중복되는 코드 블록 제거 (주소 범위 기반)"""
        if not blocks:
            return []

        # 주소로 정렬
        blocks.sort(key=lambda x: int(x['trigger_address'], 16))

        deduplicated = [blocks[0]]
        for block in blocks[1:]:
            last_addr = int(deduplicated[-1]['trigger_address'], 16)
            curr_addr = int(block['trigger_address'], 16)

            # 주소 차이가 100바이트 이상이면 다른 블록으로 간주
            if curr_addr - last_addr > 100:
                deduplicated.append(block)

        return deduplicated

    def _format_for_llm(
        self,
        filename: str,
        binary_size: int,
        crypto_strings: List[Dict],
        disasm_blocks: List[Dict]
    ) -> str:
        """LLM이 분석하기 쉬운 마크다운 형식으로 포맷팅"""

        output = []
        output.append(f"# Binary Analysis: {filename}")
        output.append(f"**Binary Size**: {binary_size:,} bytes\n")

        # 1. 요약
        output.append("## 🔍 Analysis Summary")
        output.append(f"- Suspicious strings found: {len(crypto_strings)}")
        output.append(f"- Suspicious code blocks found: {len(disasm_blocks)}")
        output.append("")

        # 2. 암호화 관련 문자열 (상위 20개만)
        if crypto_strings:
            output.append("## 📝 Cryptography-Related Strings")
            for i, item in enumerate(crypto_strings[:20], 1):
                output.append(f"\n### String {i} (confidence: {item['confidence']})")
                output.append(f"```\n{item['string']}\n```")
                if item['keywords']:
                    output.append(f"Matched keywords: `{', '.join(item['keywords'])}`")
                if item['functions']:
                    output.append(f"Matched functions: `{', '.join(item['functions'])}`")

        # 3. 의심스러운 어셈블리 코드 블록 (상위 10개만)
        if disasm_blocks:
            output.append("\n## ⚙️ Suspicious Assembly Code Blocks")
            for i, block in enumerate(disasm_blocks[:10], 1):
                output.append(f"\n### Block {i} at {block['trigger_address']} (confidence: {block['confidence']:.2f})")
                output.append(f"**Trigger**: `{block['trigger_instruction']}`")
                output.append(f"```asm\n{block['context']}\n```")

        # 최종 텍스트 생성
        full_output = '\n'.join(output)

        # 컨텍스트 크기 제한
        if len(full_output) > self.max_context_chars:
            print(f"   ⚠️ 출력 크기 초과 ({len(full_output)} chars), {self.max_context_chars} chars로 축약")
            full_output = full_output[:self.max_context_chars] + "\n\n... (truncated for LLM context limit)"

        return full_output


# 싱글톤 인스턴스
_preprocessor_instance: Optional[BinaryPreprocessor] = None

def get_binary_preprocessor() -> BinaryPreprocessor:
    """바이너리 전처리기 싱글톤 인스턴스 반환"""
    global _preprocessor_instance
    if _preprocessor_instance is None:
        _preprocessor_instance = BinaryPreprocessor()
    return _preprocessor_instance
