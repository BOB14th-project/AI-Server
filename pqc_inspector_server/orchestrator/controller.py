# File: pqc_inspector_server/orchestrator/controller.py
# 🧠 파일 분류, 에이전트 호출, 결과 취합 및 DB 저장을 총괄하는 오케스트레이터 컨트롤러입니다.

from fastapi import UploadFile, Depends
from typing import Optional

# --- 의존성 임포트 변경 및 추가 ---
from ..db.api_client import ExternalAPIClient, get_api_client
from ..agents.source_code import SourceCodeAgent
from ..agents.assembly_binary import AssemblyBinaryAgent
from ..agents.logs_config import LogsConfigAgent
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
            "assembly_binary": AssemblyBinaryAgent(),
            "logs_config": LogsConfigAgent()
        }
        print("OrchestratorController가 AI 오케스트레이터와 함께 초기화되었습니다.")

    async def analyze_all_files_from_db(self, scan_id: int, max_files: int = 100):
        """
        DB에 있는 모든 파일을 자동으로 검사합니다.
        file_id를 1부터 max_files까지 순회하며 데이터가 있는 파일만 분석합니다.
        """
        print("=" * 80)
        print(f"🚀 [전체 파일 분석 시작] Scan ID: {scan_id}, 최대 파일: {max_files}")
        print("=" * 80)

        results = []
        total_attempted = 0
        total_success = 0
        total_failed = 0

        for file_id in range(1, max_files + 1):
            total_attempted += 1
            print(f"\n{'='*80}")
            print(f"📁 [{total_attempted}/{max_files}] File ID {file_id} 분석 시도 중...")
            print(f"{'='*80}")

            try:
                result = await self.analyze_from_db(file_id, scan_id)

                if result.get("success"):
                    total_success += 1
                    print(f"✅ File ID {file_id} 분석 성공")
                    results.append({
                        "file_id": file_id,
                        "status": "success",
                        "message": "분석 완료"
                    })
                else:
                    # 데이터가 없는 경우 - 실패로 카운트하지 않음
                    error_msg = result.get("error", "")
                    if "데이터가 없습니다" in error_msg:
                        print(f"⏭️  File ID {file_id} - 데이터 없음, 건너뜀")
                        total_attempted -= 1  # 실제 시도 횟수에서 제외
                    else:
                        total_failed += 1
                        print(f"❌ File ID {file_id} 분석 실패: {error_msg}")
                        results.append({
                            "file_id": file_id,
                            "status": "failed",
                            "error": error_msg
                        })

            except Exception as e:
                total_failed += 1
                print(f"❌ File ID {file_id} 분석 중 예외 발생: {e}")
                results.append({
                    "file_id": file_id,
                    "status": "error",
                    "error": str(e)
                })

        print("\n" + "=" * 80)
        print(f"🎉 [전체 분석 완료]")
        print(f"   - 총 시도: {total_attempted}개 파일")
        print(f"   - 성공: {total_success}개")
        print(f"   - 실패: {total_failed}개")
        print("=" * 80)

        return {
            "scan_id": scan_id,
            "total_attempted": total_attempted,
            "total_success": total_success,
            "total_failed": total_failed,
            "results": results
        }

    async def analyze_from_db(self, file_id: int, scan_id: int):
        """
        DB에서 모든 데이터를 가져와서 종합 분석을 수행하고 결과를 DB에 저장합니다.
        이것이 메인 분석 엔드포인트입니다.
        """
        print("=" * 80)
        print(f"🚀 [DB 기반 분석 시작] File ID: {file_id}, Scan ID: {scan_id}")
        print("=" * 80)

        try:
            # 1단계: DB에서 모든 데이터 가져오기
            print("\n🔍 [1단계] DB에서 데이터 조회 중...")
            db_data = await self.api_client.get_all_file_data(file_id, scan_id)

            assembly_text = db_data.get("assembly_text")
            generated_code = db_data.get("generated_code")
            logs = db_data.get("logs")

            if not assembly_text and not generated_code and not logs:
                print("❌ DB에 데이터가 없습니다.")
                return {
                    "success": False,
                    "error": "DB에 분석할 데이터가 없습니다."
                }

            print(f"✅ [1단계 완료] 데이터 조회 성공")
            print(f"   - 어셈블리: {len(assembly_text) if assembly_text else 0} bytes")
            print(f"   - 코드: {len(generated_code) if generated_code else 0} bytes")
            print(f"   - 로그: {len(logs) if logs else 0} bytes")

            # 2단계: 각 에이전트로 분석 수행
            print("\n🔬 [2단계] 에이전트별 분석 시작...")
            agent_results = []

            # 어셈블리/바이너리 분석
            if assembly_text:
                print("   🤖 Assembly/Binary Agent 분석 중...")
                assembly_agent = self.agents["assembly_binary"]
                assembly_result = await assembly_agent.analyze(
                    assembly_text.encode('utf-8'),
                    f"file_{file_id}_assembly"
                )
                agent_results.append({
                    "type": "assembly_binary",
                    "result": assembly_result
                })
                print(f"   ✅ Assembly 분석 완료 - 취약점: {assembly_result.get('is_pqc_vulnerable')}")

            # 소스코드 분석
            if generated_code:
                print("   🤖 Source Code Agent 분석 중...")
                source_agent = self.agents["source_code"]
                code_result = await source_agent.analyze(
                    generated_code.encode('utf-8'),
                    f"file_{file_id}_code.py"
                )
                agent_results.append({
                    "type": "source_code",
                    "result": code_result
                })
                print(f"   ✅ Source Code 분석 완료 - 취약점: {code_result.get('is_pqc_vulnerable')}")

            # 로그 분석
            if logs:
                print("   🤖 Logs/Config Agent 분석 중...")
                logs_agent = self.agents["logs_config"]
                logs_result = await logs_agent.analyze(
                    logs.encode('utf-8'),
                    f"file_{file_id}_logs.log"
                )
                agent_results.append({
                    "type": "logs_config",
                    "result": logs_result
                })
                print(f"   ✅ Logs 분석 완료 - 취약점: {logs_result.get('is_pqc_vulnerable')}")

            print(f"✅ [2단계 완료] 총 {len(agent_results)}개 에이전트 분석 완료")

            # 3단계: AI 오케스트레이터로 종합 분석
            print("\n🧠 [3단계] AI 오케스트레이터 종합 분석 시작...")
            comprehensive_analysis = await self._create_comprehensive_analysis(
                file_id, scan_id, db_data, agent_results
            )
            print("✅ [3단계 완료] 종합 분석 완료")

            # 4단계: DB에 최종 분석 결과 저장
            print("\n💾 [4단계] DB에 최종 분석 결과 저장 중...")
            save_success = await self.api_client.save_llm_analysis(
                file_id, scan_id, comprehensive_analysis
            )

            if save_success:
                print("✅ [4단계 완료] 분석 결과 저장 성공")
                print("=" * 80)
                print(f"🎉 [완료] File ID [{file_id}], Scan ID [{scan_id}] 전체 분석 프로세스 완료!")
                print("=" * 80)

                # 프론트엔드 응답용 데이터
                return {
                    "success": True,
                    "file_id": file_id,
                    "scan_id": scan_id,
                    "message": "분석이 완료되어 DB에 저장되었습니다.",
                    "analysis_preview": comprehensive_analysis[:500] + "..." if len(comprehensive_analysis) > 500 else comprehensive_analysis
                }
            else:
                print("❌ [4단계 실패] DB 저장 실패")
                return {
                    "success": False,
                    "error": "분석 결과 DB 저장 실패"
                }

        except Exception as e:
            print(f"❌ [오류] 분석 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_comprehensive_analysis(
        self,
        file_id: int,
        scan_id: int,
        db_data: dict,
        agent_results: list
    ) -> str:
        """
        AI 오케스트레이터를 사용하여 모든 에이전트 결과를 종합한 상세한 분석 리포트를 생성합니다.
        """
        try:
            # 에이전트 결과 요약
            results_summary = []
            for agent_result in agent_results:
                agent_type = agent_result["type"]
                result = agent_result["result"]
                results_summary.append({
                    "agent_type": agent_type,
                    "is_vulnerable": result.get("is_pqc_vulnerable", False),
                    "detected_algorithms": result.get("detected_algorithms", []),
                    "confidence": result.get("confidence_score", 0.0),
                    "details": result.get("vulnerability_details", ""),
                    "recommendations": result.get("recommendations", "")
                })

            comprehensive_prompt = f"""당신은 양자컴퓨팅 보안 전문가입니다.
다음 파일(File ID: {file_id}, Scan ID: {scan_id})에 대한 다중 에이전트 분석 결과를 종합하여
프론트엔드에서 활용할 수 있도록 구조화된 보안 분석 리포트를 작성해주세요.

=== 분석 데이터 ===
어셈블리 코드: {len(db_data.get('assembly_text', '')) if db_data.get('assembly_text') else 0} bytes
생성된 코드: {len(db_data.get('generated_code', '')) if db_data.get('generated_code') else 0} bytes
로그: {len(db_data.get('logs', '')) if db_data.get('logs') else 0} bytes

=== 에이전트 분석 결과 ===
{json.dumps(results_summary, ensure_ascii=False, indent=2)}

=== 상세 데이터 미리보기 ===
어셈블리: {db_data.get('assembly_text', '')[:500] if db_data.get('assembly_text') else 'N/A'}
코드: {db_data.get('generated_code', '')[:500] if db_data.get('generated_code') else 'N/A'}
로그: {db_data.get('logs', '')[:500] if db_data.get('logs') else 'N/A'}

**중요: 다음 3개 카테고리로 명확하게 구분하여 작성해주세요. 프론트엔드에서 파싱할 것입니다.**

리포트는 반드시 다음 마크다운 구조를 따라야 합니다:

---

# 1. 스캔 대상

**File ID**: {file_id}
**Scan ID**: {scan_id}

## 1.1 파일 정보
- **분석 대상 파일**: [파일명 또는 식별자]
- **파일 타입**: [어셈블리/소스코드/로그 등]
- **파일 크기**: [바이트 단위]
- **분석 일시**: [현재 날짜/시간]

## 1.2 검사 범위
- **검사한 암호 알고리즘**: [탐지된 알고리즘 나열]
- **분석 레벨**: [어셈블리/소스코드/로그 중 수행된 것]
- **사용된 AI 에이전트**: [실행된 에이전트 목록]

## 1.3 전체 요약
- **보안 상태**: [양호/주의/위험 중 하나]
- **PQC 취약점 발견**: [예/아니오]
- **위험도 등급**: [High/Medium/Low]
- **종합 신뢰도**: [0.0-1.0 점수]

---

# 2. 상세 내용

## 2.1 발견된 취약점
[각 취약점마다 다음 형식으로 작성]

### 취약점 #1: [알고리즘명] (예: RSA-2048)
- **심각도**: [High/Medium/Low]
- **발견 위치**: [어셈블리/코드/로그]
- **탐지 근거**: [구체적인 증거 코드 또는 패턴]
- **양자컴퓨터 위협**: [Shor 알고리즘/Grover 알고리즘 등]
- **예상 피해**: [구체적인 보안 영향]

### 취약점 #2: [알고리즘명]
...

## 2.2 기술적 분석

### 어셈블리 레벨 분석
- **분석 결과**: [구체적인 발견 사항]
- **암호 함수 호출**: [탐지된 함수명]
- **코드 패턴**: [특이사항]

### 소스코드 레벨 분석
- **분석 결과**: [구체적인 발견 사항]
- **라이브러리 사용**: [사용된 암호 라이브러리]
- **구현 방식**: [특이사항]

### 로그/설정 분석
- **분석 결과**: [구체적인 발견 사항]
- **설정 이슈**: [보안 설정 문제]
- **로그 패턴**: [특이사항]

## 2.3 종합 평가
- **전반적 보안 수준**: [평가 내용]
- **주요 위험 요소**: [핵심 문제점]
- **긍정적 요소**: [잘 된 부분]

---

# 3. 전환 가이드

## 3.1 즉시 조치 필요 사항 (High Priority)
1. **[취약점명]**: [구체적 조치 방법]
2. **[취약점명]**: [구체적 조치 방법]

## 3.2 양자내성 암호 전환 로드맵

### 단기 계획 (1-3개월)
1. **현재 암호 → PQC 암호 매핑**
   - RSA-2048 → CRYSTALS-Kyber (키 교환)
   - ECDSA → CRYSTALS-Dilithium (전자서명)
   - AES-128 → AES-256 (대칭키 강화)

2. **마이그레이션 우선순위**
   - [High] [항목1]
   - [Medium] [항목2]
   - [Low] [항목3]

### 중기 계획 (3-6개월)
1. **하이브리드 암호 시스템 도입**
   - 기존 알고리즘 + PQC 알고리즘 병행
   - 점진적 전환을 통한 안정성 확보

2. **테스트 및 검증**
   - 성능 테스트
   - 호환성 검증
   - 보안 감사

### 장기 계획 (6-12개월)
1. **완전한 PQC 전환**
   - 모든 레거시 암호 제거
   - PQC 표준 준수
   - 지속적 모니터링 체계 구축

## 3.3 권장 라이브러리 및 도구
- **NIST PQC 표준 라이브러리**: [구체적인 라이브러리명과 버전]
- **호환성 도구**: [마이그레이션 도구]
- **모니터링 도구**: [보안 검사 도구]

## 3.4 추가 리소스
- **NIST PQC 프로젝트**: [관련 문서 링크]
- **마이그레이션 가이드**: [참고 자료]
- **기술 지원**: [전문가 연락처 또는 커뮤니티]

---

**리포트 작성 완료**
**생성 일시**: [현재 시간]
**담당 AI**: PQC Inspector AI Orchestrator

---

위 형식을 정확히 따라 마크다운으로 작성해주세요. 각 섹션은 반드시 `# 1. 스캔 대상`, `# 2. 상세 내용`, `# 3. 전환 가이드`로 시작해야 합니다."""

            # AI 오케스트레이터 호출
            orchestrator_response = await self.ai_service.generate_response(
                model=self.orchestrator_model,
                prompt=comprehensive_prompt,
                system_prompt="당신은 양자컴퓨팅 보안 전문가이자 다중 에이전트 분석 결과를 종합하는 오케스트레이터입니다. 여러 소스의 분석 결과를 통합하여 포괄적이고 실용적인 보안 리포트를 작성합니다."
            )

            if orchestrator_response.get("success"):
                comprehensive_analysis = orchestrator_response["content"]
                print("   ✅ 오케스트레이터 종합 분석 생성 완료")
                return comprehensive_analysis
            else:
                # AI 실패시 기본 리포트 생성
                print(f"   ⚠️ AI 종합 분석 실패: {orchestrator_response.get('error')}")
                return self._create_fallback_analysis(file_id, scan_id, agent_results)

        except Exception as e:
            print(f"   ❌ 종합 분석 생성 중 오류: {e}")
            return self._create_fallback_analysis(file_id, scan_id, agent_results)

    def _create_fallback_analysis(self, file_id: int, scan_id: int, agent_results: list) -> str:
        """AI 오케스트레이터 실패시 기본 분석 리포트를 생성합니다."""
        report_lines = [
            f"# PQC 보안 분석 리포트",
            f"",
            f"**File ID:** {file_id}",
            f"**Scan ID:** {scan_id}",
            f"",
            f"## 에이전트 분석 결과",
            f""
        ]

        for agent_result in agent_results:
            agent_type = agent_result["type"]
            result = agent_result["result"]

            report_lines.append(f"### {agent_type.upper()}")
            report_lines.append(f"- **취약점 발견:** {result.get('is_pqc_vulnerable', False)}")
            report_lines.append(f"- **탐지된 알고리즘:** {', '.join(result.get('detected_algorithms', []))}")
            report_lines.append(f"- **신뢰도:** {result.get('confidence_score', 0.0):.2f}")
            report_lines.append(f"- **상세:** {result.get('vulnerability_details', 'N/A')}")
            report_lines.append(f"")

        report_lines.append("## 결론")
        report_lines.append("다중 에이전트 분석이 완료되었습니다. 상세 내용은 위 결과를 참조하세요.")

        return "\n".join(report_lines)

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
2. assembly_binary: 실행 파일, 라이브러리, 어셈블리 코드 (.exe, .so, .dll, .asm 등)
3. logs_config: 로그 파일, 서버 설정 (.log, .conf, .ini 등)

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
                        valid_types = ["source_code", "assembly_binary", "logs_config"]
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
            '.log': 'logs_config', '.conf': 'logs_config', '.txt': 'logs_config',
            '.json': 'logs_config', '.yaml': 'logs_config', '.yml': 'logs_config', '.xml': 'logs_config',
            '.toml': 'logs_config', '.ini': 'logs_config', '.cfg': 'logs_config', '.config': 'logs_config'
        }

        file_ext = "." + filename.split('.')[-1].lower()
        file_type = extension_map.get(file_ext, "assembly_binary")

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
            # 외부 API에 최종 결과 저장 (레거시 지원)
            print(f"\n💾 [4단계] 분석 완료")
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
2. assembly_binary: 실행 파일, 라이브러리, 어셈블리 코드 (.exe, .so, .dll, .asm 등)
3. logs_config: 로그 파일, 서버 설정 (.log, .conf, .ini 등)

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
                        valid_types = ["source_code", "assembly_binary", "logs_config"]
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
        주어진 작업 ID에 해당하는 분석 결과를 외부 API에서 조회합니다. (레거시)
        """
        print(f"작업 ID [{task_id}] - 레거시 메서드 호출")
        return None

# FastAPI의 의존성 주입(Dependency Injection) 시스템을 위한 함수입니다.
# 외부 API 클라이언트를 컨트롤러에 주입합니다.
def get_orchestrator_controller(api_client: ExternalAPIClient = Depends(get_api_client)):
    return OrchestratorController(api_client=api_client)
