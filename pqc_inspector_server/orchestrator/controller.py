# File: pqc_inspector_server/orchestrator/controller.py
# 🧠 파일 분류, 에이전트 호출, 결과 취합 및 DB 저장을 총괄하는 오케스트레이터 컨트롤러입니다.

from fastapi import UploadFile, Depends

# --- 의존성 임포트 변경 및 추가 ---
from ..db.api_client import ExternalAPIClient, get_api_client
from ..agents.source_code import SourceCodeAgent
from ..agents.binary import BinaryAgent
from ..agents.log_conf import LogConfAgent
from ..api.schemas import AnalysisResultCreate
from ..services.ai_service import AIService, get_ai_service
from ..core.config import settings
import json

class OrchestratorController:
    def __init__(self, api_client: ExternalAPIClient):
        # 의존성 주입을 통해 외부 API 클라이언트와 에이전트들을 초기화합니다.
        self.api_client = api_client
        self.ai_service = get_ai_service()
        self.orchestrator_model = settings.ORCHESTRATOR_MODEL
        self.agents = {
            "source_code": SourceCodeAgent(),
            "binary": BinaryAgent(),
            "log_conf": LogConfAgent()
        }
        print("OrchestratorController가 AI 오케스트레이터와 함께 초기화되었습니다.")

    async def classify_file_type(self, file: UploadFile) -> str:
        """
        AI 오케스트레이터를 사용하여 업로드된 파일의 타입을 지능적으로 분류합니다.
        파일명, 확장자, 내용을 종합적으로 분석합니다.
        """
        if not file.filename:
            return "unknown"

        try:
            # 파일 내용 읽기 (처음 1KB만)
            content = await file.read(1024)
            await file.seek(0)  # 포인터 초기화
            
            # 텍스트 변환 시도
            try:
                content_preview = content.decode('utf-8')
            except UnicodeDecodeError:
                # 바이너리 파일의 경우 헥스 미리보기
                content_preview = f"Binary file (hex preview): {content[:50].hex()}"

            # AI 오케스트레이터 프롬프트
            classification_prompt = f"""파일 분류 전문가로서 다음 파일을 분석하여 적절한 카테고리로 분류해주세요.

파일 정보:
- 파일명: {file.filename}
- 크기: {len(content)} bytes
- 내용 미리보기:
```
{content_preview[:500]}
```

분류 카테고리:
1. source_code: 프로그래밍 언어 소스코드 (.py, .java, .c, .go, .js 등)
2. binary: 실행 파일, 라이브러리 (.exe, .so, .dll 등)
3. log_conf: 로그 파일, 서버 설정 (.log, .conf, .ini 등)

JSON 형식으로만 응답:
{{"file_type": "카테고리명", "confidence": 0.0-1.0, "reasoning": "분류 근거"}}"""

            # AI 모델 호출
            ai_response = await self.ai_service.generate_response(
                model=self.orchestrator_model,
                prompt=classification_prompt,
                system_prompt="당신은 파일 타입 분류 전문가입니다. 파일명, 확장자, 내용을 종합적으로 분석하여 정확한 분류를 수행합니다."
            )

            if ai_response.get("success"):
                try:
                    # JSON 응답 파싱
                    response_text = ai_response["content"]
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                        classification_result = json.loads(json_text)
                        
                        file_type = classification_result.get("file_type", "unknown")
                        confidence = classification_result.get("confidence", 0.0)
                        reasoning = classification_result.get("reasoning", "")
                        
                        # 유효한 타입인지 검증
                        valid_types = ["source_code", "binary", "log_conf"]
                        if file_type not in valid_types:
                            file_type = self._fallback_classification(file.filename)
                        
                        print(f"AI 분류 결과 - 파일: '{file.filename}' → 타입: '{file_type}' (신뢰도: {confidence:.2f})")
                        print(f"분류 근거: {reasoning}")
                        
                        return file_type
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"AI 분류 응답 파싱 실패: {e}")
                    return self._fallback_classification(file.filename)
            else:
                print(f"AI 분류 실패: {ai_response.get('error')}")
                return self._fallback_classification(file.filename)
                
        except Exception as e:
            print(f"파일 분류 중 오류 발생: {e}")
            return self._fallback_classification(file.filename)

    def _fallback_classification(self, filename: str) -> str:
        """AI 분류 실패시 확장자 기반 폴백 분류"""
        if not filename:
            return "unknown"
            
        extension_map = {
            '.py': 'source_code', '.java': 'source_code', '.c': 'source_code', '.cpp': 'source_code',
            '.go': 'source_code', '.js': 'source_code', '.ts': 'source_code', '.rs': 'source_code',
            '.log': 'log_conf', '.conf': 'log_conf', '.txt': 'log_conf',
            '.json': 'log_conf', '.yaml': 'log_conf', '.yml': 'log_conf', '.xml': 'log_conf',
            '.toml': 'log_conf', '.ini': 'log_conf', '.cfg': 'log_conf', '.config': 'log_conf'
        }
        
        file_ext = "." + filename.split('.')[-1].lower()
        file_type = extension_map.get(file_ext, "binary")
        
        print(f"폴백 분류: '{filename}' → '{file_type}' (확장자 기반)")
        return file_type

    async def start_analysis_with_content(self, filename: str, file_content: bytes, task_id: str):
        """
        파일 내용을 받아서 분석 프로세스 전체를 관리하는 메인 메소드입니다.
        AI 오케스트레이터가 분류, 분석, 검증, 요약까지 수행합니다.
        """
        print("=" * 80)
        print(f"🚀 [작업 ID: {task_id}] PQC 분석 시작")
        print(f"📁 파일명: {filename}")
        print(f"📏 파일 크기: {len(file_content):,} bytes")
        print("=" * 80)
        
        # 1단계: AI 기반 파일 분류
        print("\n🔍 [1단계] AI 오케스트레이터 파일 분류 시작...")
        file_type = await self._classify_file_type_from_content(filename, file_content)
        print(f"✅ [1단계 완료] 파일 타입: {file_type}")
        
        agent = self.agents.get(file_type)
        final_result = None

        if agent:
            try:
                # 2단계: 전문 에이전트 분석
                print(f"\n🔬 [2단계] {file_type.upper()} 전문 에이전트 분석 시작...")
                print(f"🤖 사용 에이전트: {agent.__class__.__name__}")
                
                agent_result = await agent.analyze(file_content, filename)
                
                print(f"✅ [2단계 완료] 에이전트 분석 결과:")
                print(f"   - 취약점 발견: {agent_result.get('is_pqc_vulnerable', 'Unknown')}")
                print(f"   - 신뢰도: {agent_result.get('confidence_score', 0):.2f}")
                
                # 3단계: AI 오케스트레이터 결과 검증 및 요약
                print(f"\n🧠 [3단계] AI 오케스트레이터 결과 검증 및 요약 시작...")
                validated_result = await self._validate_and_summarize_result(
                    filename, file_type, agent_result, file_content
                )
                print(f"✅ [3단계 완료] 오케스트레이터 검증 완료")
                
                # 최종 결과 모델 생성
                final_result = AnalysisResultCreate(
                    file_name=filename,
                    file_type=file_type,
                    **validated_result
                )
                
                print(f"\n📊 [최종 결과]")
                print(f"   - 파일: {filename}")
                print(f"   - 타입: {file_type}")
                print(f"   - PQC 취약점: {validated_result.get('is_pqc_vulnerable')}")
                print(f"   - 탐지된 알고리즘: {validated_result.get('detected_algorithms', [])}")
                print(f"   - 최종 신뢰도: {validated_result.get('confidence_score', 0):.2f}")

            except Exception as e:
                print(f"❌ [오류] 작업 ID [{task_id}] - 분석 중 오류 발생: {e}")
                # 오류 발생시에도 기본 결과 생성
                final_result = self._create_error_result(filename, file_type, str(e))
        else:
            print(f"❌ [오류] 작업 ID [{task_id}] - '{file_type}' 타입을 처리할 에이전트가 없습니다.")
            final_result = self._create_error_result(filename, file_type, "지원하지 않는 파일 타입")

        if final_result:
            # 외부 API에 최종 결과 저장
            print(f"\n💾 [4단계] 외부 API에 결과 저장 중...")
            await self.api_client.save_analysis_result(task_id, final_result.model_dump())
            print(f"✅ [4단계 완료] 분석 결과 저장됨")
            print("=" * 80)
            print(f"🎉 [완료] 작업 ID [{task_id}] 전체 분석 프로세스 완료!")
            print("=" * 80)
        else:
            print(f"❌ [실패] 작업 ID [{task_id}] - 분석 결과 생성 실패")
            print("=" * 80)

    async def _classify_file_type_from_content(self, filename: str, content: bytes) -> str:
        """
        AI 오케스트레이터를 사용하여 파일 내용으로부터 타입을 분류합니다.
        """
        try:
            # 텍스트 변환 시도
            try:
                content_preview = content.decode('utf-8')
            except UnicodeDecodeError:
                # 바이너리 파일의 경우 헥스 미리보기
                content_preview = f"Binary file (hex preview): {content[:50].hex()}"

            # AI 오케스트레이터 프롬프트
            classification_prompt = f"""파일 분류 전문가로서 다음 파일을 분석하여 적절한 카테고리로 분류해주세요.

파일 정보:
- 파일명: {filename}
- 크기: {len(content)} bytes
- 내용 미리보기:
```
{content_preview[:500]}
```

분류 카테고리:
1. source_code: 프로그래밍 언어 소스코드 (.py, .java, .c, .go, .js 등)
2. binary: 실행 파일, 라이브러리 (.exe, .so, .dll 등)
3. log_conf: 로그 파일, 서버 설정 (.log, .conf, .ini 등)

JSON 형식으로만 응답:
{{"file_type": "카테고리명", "confidence": 0.0-1.0, "reasoning": "분류 근거"}}"""

            # AI 모델 호출
            ai_response = await self.ai_service.generate_response(
                model=self.orchestrator_model,
                prompt=classification_prompt,
                system_prompt="당신은 파일 타입 분류 전문가입니다. 파일명, 확장자, 내용을 종합적으로 분석하여 정확한 분류를 수행합니다."
            )

            if ai_response.get("success"):
                try:
                    # JSON 응답 파싱
                    response_text = ai_response["content"]
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                        classification_result = json.loads(json_text)
                        
                        file_type = classification_result.get("file_type", "unknown")
                        confidence = classification_result.get("confidence", 0.0)
                        reasoning = classification_result.get("reasoning", "")
                        
                        # 유효한 타입인지 검증
                        valid_types = ["source_code", "binary", "log_conf"]
                        if file_type not in valid_types:
                            file_type = self._fallback_classification(filename)
                        
                        print(f"AI 분류 결과 - 파일: '{filename}' → 타입: '{file_type}' (신뢰도: {confidence:.2f})")
                        print(f"분류 근거: {reasoning}")
                        
                        return file_type
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"AI 분류 응답 파싱 실패: {e}")
                    return self._fallback_classification(filename)
            else:
                print(f"AI 분류 실패: {ai_response.get('error')}")
                return self._fallback_classification(filename)
                
        except Exception as e:
            print(f"파일 분류 중 오류 발생: {e}")
            return self._fallback_classification(filename)

    async def _validate_and_summarize_result(self, filename: str, file_type: str, agent_result: dict, file_content: bytes) -> dict:
        """
        AI 오케스트레이터가 에이전트 결과를 검증하고 요약합니다.
        """
        try:
            # 파일 내용을 텍스트로 변환 (미리보기용)
            try:
                content_preview = file_content[:500].decode('utf-8')
            except UnicodeDecodeError:
                content_preview = f"Binary file (hex): {file_content[:100].hex()}"

            validation_prompt = f"""PQC 분석 결과 검증 전문가로서 다음 분석 결과를 검토하고 최종 요약을 제공해주세요.

파일 정보:
- 파일명: {filename}
- 파일 타입: {file_type}
- 내용 미리보기: {content_preview}

에이전트 분석 결과:
{json.dumps(agent_result, ensure_ascii=False, indent=2)}

검증 기준:
1. 취약점 탐지의 정확성
2. 신뢰도 점수의 적절성  
3. 권장사항의 실용성
4. 증거 자료의 유효성

최종 검증된 결과를 JSON 형식으로 반환:
{{
    "is_pqc_vulnerable": true/false,
    "vulnerability_details": "검증된 취약점 설명",
    "detected_algorithms": ["알고리즘 목록"],
    "recommendations": "개선된 권장사항",
    "evidence": "핵심 증거",
    "confidence_score": 0.0-1.0,
    "orchestrator_summary": "오케스트레이터 종합 의견"
}}"""

            # AI 오케스트레이터 검증
            validation_response = await self.ai_service.generate_response(
                model=self.orchestrator_model,
                prompt=validation_prompt,
                system_prompt="당신은 PQC 분석 결과를 검증하고 품질을 보장하는 오케스트레이터입니다. 에이전트 결과를 객관적으로 평가하고 개선된 최종 결과를 제공합니다."
            )

            if validation_response.get("success"):
                try:
                    response_text = validation_response["content"]
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_text = response_text[json_start:json_end]
                        validated_result = json.loads(json_text)
                        
                        print(f"오케스트레이터 검증 완료 - 파일: {filename}")
                        print(f"최종 신뢰도: {validated_result.get('confidence_score', 0.0):.2f}")
                        
                        return validated_result
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"검증 결과 파싱 실패: {e}")
                    # 원본 에이전트 결과에 오케스트레이터 요약 추가
                    agent_result["orchestrator_summary"] = "검증 과정에서 파싱 오류 발생"
                    return agent_result
            else:
                print(f"검증 과정 실패: {validation_response.get('error')}")
                agent_result["orchestrator_summary"] = "AI 검증 실패로 원본 결과 반환"
                return agent_result
                
        except Exception as e:
            print(f"결과 검증 중 오류: {e}")
            agent_result["orchestrator_summary"] = f"검증 중 오류 발생: {str(e)}"
            return agent_result

    def _create_error_result(self, filename: str, file_type: str, error_detail: str) -> AnalysisResultCreate:
        """오류 발생시 기본 결과를 생성합니다."""
        return AnalysisResultCreate(
            file_name=filename,
            file_type=file_type,
            is_pqc_vulnerable=False,
            vulnerability_details=f"분석 실패: {error_detail}",
            detected_algorithms=[],
            recommendations="수동 검토 필요",
            evidence=f"오류 파일: {filename}",
            confidence_score=0.0
        )

    async def get_analysis_result(self, task_id: str):
        """
        주어진 작업 ID에 해당하는 분석 결과를 외부 API에서 조회합니다.
        """
        print(f"작업 ID [{task_id}] - 외부 API에서 분석 결과를 조회합니다.")
        return await self.api_client.get_analysis_result(task_id)

# FastAPI의 의존성 주입(Dependency Injection) 시스템을 위한 함수입니다.
# 외부 API 클라이언트를 컨트롤러에 주입합니다.
def get_orchestrator_controller(api_client: ExternalAPIClient = Depends(get_api_client)):
    return OrchestratorController(api_client=api_client)