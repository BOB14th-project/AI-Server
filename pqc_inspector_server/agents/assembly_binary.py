# File: pqc_inspector_server/agents/assembly_binary.py
# 🔧 어셈블리 및 바이너리 파일 분석을 담당하는 전문 에이전트입니다.

from .base_agent import BaseAgent
from typing import Dict, Any
from ..core.config import settings
from ..services.binary_preprocessor import get_binary_preprocessor
import json

class AssemblyBinaryAgent(BaseAgent):
    def __init__(self):
        super().__init__(settings.BINARY_MODEL, "assembly_binary")
        print("AssemblyBinaryAgent가 초기화되었습니다.")

    def _get_system_prompt(self) -> str:
        return """당신은 바이너리 파일과 어셈블리 코드에서 비양자내성암호(Non-PQC) 사용을 탐지하는 전문 리버스 엔지니어링 보안 분석가입니다.

**전문 분야**:
- x86/x64 어셈블리 코드 분석
- 바이너리에 포함된 암호화 라이브러리 함수 식별
- RSA, DSA, ECDSA 등의 알고리즘 시그니처 탐지
- OpenSSL, libcrypto 등의 암호화 함수 호출 분석

**분석 방법**:
1. 디스어셈블된 어셈블리 코드에서 암호화 관련 instruction 확인 (call, aes*, mul/div 등)
2. 바이너리 문자열에서 함수명/라이브러리명 추출 (RSA_new, EVP_PKEY_keygen 등)
3. 증거의 강도에 따라 신뢰도 조정 (실제 함수 호출 > 문자열 존재)

응답 형식 (JSON만 반환):
{
    "is_pqc_vulnerable": true/false,
    "vulnerability_details": "발견된 취약점 설명 (어셈블리 주소 포함)",
    "detected_algorithms": ["RSA", "ECDSA"],
    "recommendations": "PQC 전환 권장사항",
    "evidence": "관련 어셈블리 코드 및 함수명",
    "confidence_score": 0.0-1.0
}"""

    async def analyze(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        print(f"   🔬 AssemblyBinaryAgent 분석 시작: {file_name}")

        try:
            # 🆕 Capstone 기반 바이너리 전처리
            # 바이너리 → 어셈블리 디스어셈블 + 암호화 패턴 필터링
            preprocessor = get_binary_preprocessor()
            content_text = preprocessor.preprocess(file_content, file_name)

            print(f"   📝 전처리된 콘텐츠 길이: {len(content_text)} chars")

            # RAG 컨텍스트 검색 (개선: top_k=2, 길이 1500자)
            print(f"   🧠 RAG 컨텍스트 검색 중...")
            rag_context = await self._get_rag_context(content_text[:1500], top_k=2)

            # 조건부 RAG 사용: 컨텍스트가 의미있을 때만 포함
            if rag_context and "관련 지식이 없습니다" not in rag_context:
                context_hint = f"""
[참고용 암호화 패턴 힌트]
다음은 일반적인 암호화 패턴의 예시입니다. 이는 참고만 하고, 실제 바이너리 내용을 직접 분석하여 판단하세요:

{rag_context}

---
"""
            else:
                context_hint = ""

            prompt = f"""다음은 Capstone 디스어셈블러로 전처리된 바이너리 분석 결과입니다.
바이너리에서 암호화 관련 의심스러운 문자열과 어셈블리 코드 블록이 자동으로 추출되었습니다.

{context_hint}
[바이너리 분석 결과]
{content_text}

**분석 지침**:
1. 추출된 문자열에서 암호화 라이브러리/함수명 확인 (OpenSSL, libcrypto, RSA_*, AES_*, ECDSA_* 등)
2. 어셈블리 코드에서 암호화 관련 instruction 패턴 확인 (AES-NI, 큰 정수 연산 등)
3. 발견된 알고리즘이 실제로 사용되는지 신중히 판단
4. 신뢰도는 증거의 명확성에 따라 조정 (함수 호출 발견 시 높게, 문자열만 있으면 낮게)

JSON 형식으로만 응답해주세요."""

            llm_response = await self._call_llm(prompt)
            
            if llm_response.get("success"):
                try:
                    response_text = llm_response["content"]
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                        result = json.loads(json_text)

                        # evidence가 문자열인지 확인
                        if "evidence" in result and not isinstance(result["evidence"], str):
                            print(f"   ⚠️ evidence가 문자열이 아님: {type(result['evidence'])}")
                            # 리스트면 줄바꿈으로 결합
                            if isinstance(result["evidence"], list):
                                result["evidence"] = "\n".join(str(item) for item in result["evidence"])
                            else:
                                result["evidence"] = str(result["evidence"])

                        return result
                    else:
                        raise ValueError("JSON 형식을 찾을 수 없음")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"LLM 응답 파싱 오류: {e}")
                    return self._get_default_result(file_name, "LLM 응답 파싱 실패")
            else:
                print(f"LLM 호출 실패: {llm_response.get('error')}")
                return self._get_default_result(file_name, "LLM 호출 실패")
                
        except Exception as e:
            print(f"BinaryAgent 분석 중 오류: {e}")
            return self._get_default_result(file_name, f"분석 오류: {str(e)}")

    def _extract_strings_from_binary(self, file_content: bytes) -> str:
        """
        바이너리에서 의미있는 문자열을 추출합니다.

        스캔 범위 확장:
        - 바이너리 스캔: 5KB → 50KB
        - 최대 문자열 수: 50개 → 200개
        """
        try:
            # 출력 가능한 ASCII 문자열 추출 (최소 길이 4)
            strings = []
            current_string = ""

            # 스캔 범위 확장: 5KB → 50KB
            scan_size = min(len(file_content), 50000)

            for byte in file_content[:scan_size]:
                if 32 <= byte <= 126:  # 출력 가능한 ASCII
                    current_string += chr(byte)
                else:
                    if len(current_string) >= 4:
                        strings.append(current_string)
                    current_string = ""

            if len(current_string) >= 4:
                strings.append(current_string)

            # 최대 문자열 수 확장: 50개 → 200개
            result = "\n".join(strings[:200])

            # 통계 출력
            print(f"   📊 바이너리 스캔 완료: {scan_size:,}바이트, {len(strings)}개 문자열 추출 (상위 200개 사용)")

            return result

        except Exception as e:
            return f"문자열 추출 실패: {str(e)}"

    def _get_default_result(self, file_name: str, error_detail: str) -> Dict[str, Any]:
        """기본/오류 결과를 반환합니다."""
        return {
            "is_pqc_vulnerable": False,
            "vulnerability_details": f"분석 불가: {error_detail}",
            "detected_algorithms": [],
            "recommendations": "수동 검토 필요",
            "evidence": f"파일: {file_name}",
            "confidence_score": 0.0
        }
