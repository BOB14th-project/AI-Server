# File: pqc_inspector_server/agents/logs_config.py
# 📜 로그 및 설정 파일 분석을 담당하는 전문 에이전트입니다.

from .base_agent import BaseAgent
from typing import Dict, Any
from ..core.config import settings
import json

class LogsConfigAgent(BaseAgent):
    def __init__(self):
        super().__init__(settings.LOG_CONF_MODEL, "logs_config")
        print("LogsConfigAgent가 초기화되었습니다.")

    def _get_system_prompt(self) -> str:
        return """당신은 로그 파일과 설정 파일에서 비양자내성암호(Non-PQC) 사용을 탐지하는 전문 보안 분석가입니다.

주요 탐지 대상:
- TLS/SSL 연결 로그의 cipher suite 정보
- 암호화 관련 오류 메시지
- 서버 설정 파일의 암호화 설정
- 인증서 관련 로그 (RSA, ECDSA 등)

응답 형식 (JSON만 반환):
{
    "is_pqc_vulnerable": true/false,
    "vulnerability_details": "발견된 취약점 설명",
    "detected_algorithms": ["TLS_ECDHE_RSA", "RSA"],
    "recommendations": "PQC 전환 권장사항",
    "evidence": "관련 로그 라인",
    "confidence_score": 0.0-1.0
}"""

    async def analyze(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        print(f"LogConfAgent: '{file_name}' 파일 분석 중...")

        try:
            content_text = self._parse_file_content(file_content)

            # RAG 재활성화 (높은 임계값 0.20으로 관련 없는 컨텍스트 차단)
            print(f"   🧠 RAG 컨텍스트 검색 중 (임계값: 0.20)...")
            rag_context = await self._get_rag_context(content_text[:1000], top_k=3)

            # RAG 컨텍스트가 있으면 포함, 없으면 순수 LLM 판단
            if rag_context:
                prompt = f"""다음 로그/설정 파일을 분석하여 비양자내성암호 사용 여부를 확인해주세요.

{rag_context}

위의 전문가 지식을 참고하여 다음 로그/설정을 분석하세요:

파일명: {file_name}
내용:
```
{content_text[:2000]}  # 처음 2000자만 분석
```

JSON 형식으로만 응답해주세요."""
            else:
                # 유사도 임계값 이상인 컨텍스트가 없으면 순수 LLM 판단
                print(f"   ℹ️ 관련 컨텍스트 없음, 순수 LLM 분석 진행")
                prompt = f"""다음 로그/설정 파일을 분석하여 비양자내성암호 사용 여부를 확인해주세요.

파일명: {file_name}
내용:
```
{content_text[:2000]}  # 처음 2000자만 분석
```

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
            print(f"LogConfAgent 분석 중 오류: {e}")
            return self._get_default_result(file_name, f"분석 오류: {str(e)}")

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
