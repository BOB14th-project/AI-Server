# File: pqc_inspector_server/agents/source_code.py
# 👨‍💻 소스코드 분석을 담당하는 전문 에이전트입니다.

from .base_agent import BaseAgent
from typing import Dict, Any
from ..core.config import settings
import json

class SourceCodeAgent(BaseAgent):
    def __init__(self):
        super().__init__(settings.SOURCE_CODE_MODEL, "source_code")
        print("SourceCodeAgent가 초기화되었습니다.")

    def _get_system_prompt(self) -> str:
        return """You are a security analyst specializing in detecting non-quantum-resistant cryptography in source code.

CRITICAL: You MUST respond ONLY with valid JSON. No explanations, no markdown, no additional text.

Target algorithms to detect:
- RSA, DSA, ECDSA, ECDH (vulnerable to quantum attacks)
- Related library imports and function calls
- Key generation, signing, encryption operations

Response format (JSON ONLY):
{
    "is_pqc_vulnerable": boolean,
    "vulnerability_details": "string",
    "detected_algorithms": ["array of strings"],
    "recommendations": "string", 
    "evidence": "string",
    "confidence_score": number_between_0_and_1
}"""

    async def analyze(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        print(f"   🔬 SourceCodeAgent 분석 시작: {file_name}")

        try:
            content_text = self._parse_file_content(file_content)
            print(f"   📝 소스코드 파싱 완료 (길이: {len(content_text)} chars)")

            # RAG 컨텍스트 검색
            print(f"   🧠 RAG 컨텍스트 검색 중...")
            rag_context = await self._get_rag_context(content_text[:1000], top_k=3)

            # RAG가 포함된 강화된 프롬프트 생성
            prompt = f"""Analyze the following source code file for non-quantum-resistant cryptography usage.

{rag_context}

Based on the expert knowledge above, analyze this code:

File: {file_name}
Code:
```
{content_text[:2000]}
```

You MUST respond ONLY with valid JSON in exactly this format:
{{
    "is_pqc_vulnerable": true,
    "vulnerability_details": "Found RSA 2048-bit usage",
    "detected_algorithms": ["RSA"],
    "recommendations": "Replace with CRYSTALS-Kyber",
    "evidence": "import rsa line",
    "confidence_score": 0.95
}}

Do not include any explanation or text outside the JSON."""

            print(f"   🤖 {self.model_name} 모델 호출 준비 중...")
            llm_response = await self._call_llm(prompt)

            if llm_response.get("success"):
                print(f"   ✅ {self.model_name} 응답 수신 완료")
                try:
                    # LLM 응답에서 JSON 추출 시도
                    response_text = llm_response["content"]
                    print(f"   📄 응답 내용 (처음 100자): {response_text[:100]}...")
                    
                    # 응답 내용 디버깅을 위해 출력
                    print(f"   [DEBUG] 원본 LLM 응답:")
                    print(f"   {response_text}")
                    print(f"   [DEBUG] 응답 길이: {len(response_text)}")
                    
                    # JSON 부분만 추출
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                        print(f"   [DEBUG] 추출된 JSON:")
                        print(f"   {json_text}")
                        
                        # JSON 유효성 검사를 위한 추가 처리
                        try:
                            # 잘못된 문자들 정리
                            json_text = json_text.replace('\n', ' ').replace('\r', ' ')
                            # 연속된 공백 제거
                            import re
                            json_text = re.sub(r'\s+', ' ', json_text)
                            
                            result = json.loads(json_text)

                            # evidence가 문자열인지 확인
                            if "evidence" in result and not isinstance(result["evidence"], str):
                                print(f"   ⚠️ evidence가 문자열이 아님: {type(result['evidence'])}")
                                # 리스트면 줄바꿈으로 결합
                                if isinstance(result["evidence"], list):
                                    result["evidence"] = "\n".join(str(item) for item in result["evidence"])
                                else:
                                    result["evidence"] = str(result["evidence"])

                            print(f"   [SUCCESS] JSON 파싱 성공!")
                            print(f"      - 취약점: {result.get('is_pqc_vulnerable', 'Unknown')}")
                            print(f"      - 알고리즘: {result.get('detected_algorithms', [])}")
                            return result
                            
                        except json.JSONDecodeError as json_err:
                            print(f"   [ERROR] JSON 파싱 실패: {json_err}")
                            print(f"   [ERROR] 문제가 된 JSON: {json_text}")
                            # 수동으로 기본값 생성
                            return self._create_fallback_result(response_text, file_name)
                    else:
                        raise ValueError("JSON 형식을 찾을 수 없음")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"   ❌ LLM 응답 파싱 오류: {e}")
                    # 기본값 반환
                    return self._get_default_result(file_name, "LLM 응답 파싱 실패")
            else:
                print(f"   ❌ LLM 호출 실패: {llm_response.get('error')}")
                return self._get_default_result(file_name, "LLM 호출 실패")
                
        except Exception as e:
            print(f"   ❌ SourceCodeAgent 분석 중 오류: {e}")
            return self._get_default_result(file_name, f"분석 오류: {str(e)}")

    def _create_fallback_result(self, llm_response: str, file_name: str) -> Dict[str, Any]:
        """LLM 응답을 기반으로 fallback 결과를 생성합니다."""
        # 텍스트에서 키워드 기반으로 분석 시도
        response_lower = llm_response.lower()
        
        # 키워드 탐지
        vulnerable_keywords = ['rsa', 'dsa', 'ecdsa', 'ecdh', 'vulnerable', 'true']
        safe_keywords = ['safe', 'secure', 'false', 'no vulnerability']
        algorithm_keywords = ['rsa', 'dsa', 'ecdsa', 'ecdh']
        
        is_vulnerable = any(keyword in response_lower for keyword in vulnerable_keywords)
        detected_algorithms = [alg.upper() for alg in algorithm_keywords if alg in response_lower]
        
        return {
            "is_pqc_vulnerable": is_vulnerable,
            "vulnerability_details": f"JSON 파싱 실패로 텍스트 분석: {llm_response[:200]}...",
            "detected_algorithms": detected_algorithms,
            "recommendations": "JSON 파싱 실패로 인한 추정 결과 - 수동 검토 필요",
            "evidence": f"LLM 응답 키워드 분석 기반",
            "confidence_score": 0.3  # 낮은 신뢰도
        }

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
