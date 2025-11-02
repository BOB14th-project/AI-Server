# DB 통합 가이드

AI 서버가 실제 DB API와 연동되도록 수정되었습니다.

## 변경 사항

### 1. DB API 클라이언트 (`pqc_inspector_server/db/api_client.py`)

실제 DB API 엔드포인트에 맞게 클라이언트가 수정되었습니다:

**GET 메서드:**
- `get_llm_assembly(file_id, scan_id)` - 어셈블리 텍스트 조회
- `get_llm_code(file_id, scan_id)` - 생성된 코드 조회
- `get_llm_logs(file_id, scan_id)` - 로그 조회
- `get_all_file_data(file_id, scan_id)` - 모든 데이터 병렬 조회

**POST 메서드:**
- `save_llm_assembly(file_id, scan_id, file_text)` - 어셈블리 저장
- `save_llm_analysis(file_id, scan_id, llm_analysis)` - 분석 결과 저장
- `save_llm_code(file_id, scan_id, code)` - 코드 저장
- `save_llm_log(file_id, scan_id, log)` - 로그 저장

### 2. Controller (`pqc_inspector_server/orchestrator/controller.py`)

새로운 메인 분석 메서드 추가:

**`analyze_from_db(file_id, scan_id)`:**
1. DB에서 모든 데이터 조회 (어셈블리, 코드, 로그)
2. 각 에이전트로 분석 수행
3. AI 오케스트레이터로 종합 분석 리포트 생성
4. DB에 최종 분석 결과 저장

### 3. API 엔드포인트 (`pqc_inspector_server/api/endpoints.py`)

새로운 엔드포인트 추가:

**POST `/api/v1/analyze/db`**
- Query Parameters: `file_id`, `scan_id`
- DB에서 데이터를 가져와 종합 분석 수행

### 4. 환경 설정 (`pqc_inspector_server/core/config.py`)

- `EXTERNAL_API_BASE_URL`: `https://harper-abler-agape.ngrok-free.dev`로 변경

## 사용 방법

### 기본 워크플로우

```bash
# 1. 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000

# 2. DB 기반 분석 실행 (file_id=1, scan_id=1 예시)
curl -X POST "http://localhost:8000/api/v1/analyze/db?file_id=1&scan_id=1"
```

### 응답 예시

```json
{
  "message": "분석이 성공적으로 완료되었습니다.",
  "file_id": 1,
  "scan_id": 1,
  "analysis_preview": "# PQC 보안 분석 리포트\n\n**File ID:** 1\n**Scan ID:** 1\n\n## 전체 요약 (Executive Summary)\n..."
}
```

## 분석 프로세스

### 단계별 처리

1. **DB 데이터 조회**
   - 어셈블리 텍스트, 생성된 코드, 로그를 병렬로 조회

2. **에이전트별 분석**
   - Assembly/Binary Agent: 어셈블리 코드 분석
   - Source Code Agent: 생성된 코드 분석
   - Logs/Config Agent: 로그 분석

3. **AI 오케스트레이터 종합 분석**
   - 모든 에이전트 결과를 통합
   - 상세한 보안 분석 리포트 생성
   - 마크다운 형식으로 작성

4. **DB 저장**
   - 최종 분석 결과를 DB에 저장 (`save_llm_analysis`)

## 종합 분석 리포트 구조

생성되는 리포트는 다음 내용을 포함합니다:

1. **전체 요약 (Executive Summary)**
   - 전반적인 보안 상태 평가
   - 주요 발견사항 요약

2. **발견된 취약점 상세 분석**
   - 각 에이전트가 발견한 취약점 통합 분석
   - 비양자내성 암호 알고리즘 목록 및 사용 위치
   - 위험도 평가 (High/Medium/Low)

3. **기술적 분석**
   - 어셈블리 레벨 분석 결과
   - 소스코드 레벨 분석 결과
   - 로그/설정 분석 결과
   - 각 레벨 간 연관성 분석

4. **권장사항**
   - 즉시 조치 필요 항목
   - 중장기 개선 방안
   - 양자내성 암호로의 마이그레이션 로드맵

5. **종합 신뢰도 및 결론**
   - 분석 결과의 신뢰도 평가
   - 최종 결론 및 종합 의견

## 테스트 방법

### 1. DB에 테스트 데이터가 있는 경우

```bash
# 분석 실행
curl -X POST "http://localhost:8000/api/v1/analyze/db?file_id=YOUR_FILE_ID&scan_id=YOUR_SCAN_ID"
```

### 2. DB에서 결과 확인

DB API를 통해 저장된 분석 결과를 확인할 수 있습니다:

```bash
# GET 요청으로 분석 결과 조회 (DB API 직접 호출)
curl "https://harper-abler-agape.ngrok-free.dev/files/YOUR_FILE_ID/llm_analysis/?scan_id=YOUR_SCAN_ID"
```

## 주의사항

1. **API KEY**: 현재 DB API는 인증이 필요하지 않습니다.
2. **타임아웃**: 기본 30초로 설정되어 있습니다. 큰 파일의 경우 조정이 필요할 수 있습니다.
3. **에러 처리**: 네트워크 오류나 DB 오류 시 콘솔에 로그가 출력됩니다.

## 레거시 지원

기존 파일 업로드 기반 분석도 여전히 동작합니다:

```bash
# 파일 업로드 방식 (기존)
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@your_file.py"
```

이 방식은 백그라운드에서 분석을 수행하고 task_id를 반환합니다.
