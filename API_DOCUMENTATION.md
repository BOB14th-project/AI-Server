# AI Server API 문서 (프론트엔드용)

## Base URL

### 로컬 개발
```
http://127.0.0.1:8000
```

### ngrok (외부 접속)
```
https://marvel-steamerless-downheartedly.ngrok-free.app
```

> **참고**: ngrok URL은 재시작할 때마다 변경됩니다. 최신 URL은 `.ngrok_url` 파일에서 확인하세요.

---

## 📡 핵심 API 엔드포인트

### 1. DB 기반 완전 자동 분석 (권장)

**엔드포인트**: `POST /api/v1/analyze/db`

**설명**: DB에 저장된 파일들(어셈블리, 코드, 로그)을 자동으로 가져와 분석하고, 종합 피드백을 생성하여 DB에 저장합니다.

#### 요청 파라미터
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `file_id` | integer | ✅ | 분석할 파일의 ID |
| `scan_id` | integer | ✅ | 스캔 세션 ID |

#### 요청 예시

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db?file_id=1&scan_id=1"
```

또는

```bash
curl -X POST "https://your-ngrok-url.ngrok-free.app/api/v1/analyze/db?file_id=1&scan_id=1"
```

#### 응답 (성공)

```json
{
  "message": "분석이 성공적으로 완료되었습니다.",
  "file_id": 1,
  "scan_id": 1,
  "analysis_preview": "# PQC 보안 분석 리포트\n\n**File ID:** 1\n**Scan ID:** 1\n\n## 전체 요약\n본 파일에서 비양자내성 암호 알고리즘(RSA-2048)의 사용이 확인되었습니다...\n\n(처음 500자만 미리보기)"
}
```

#### 응답 (실패)

```json
{
  "detail": "DB에 분석할 데이터가 없습니다."
}
```

또는

```json
{
  "detail": "분석 중 오류가 발생했습니다: [오류 메시지]"
}
```

---

### 프로세스 흐름

```
1. 프론트엔드가 file_id와 scan_id를 전송
   ↓
2. AI Server가 DB에서 파일 데이터 조회
   - GET /files/{file_id}/llm/?scan_id={scan_id} (어셈블리)
   - GET /files/{file_id}/llm_code/?scan_id={scan_id} (코드)
   - GET /files/{file_id}/llm_log/?scan_id={scan_id} (로그)
   ↓
3. 각 파일 타입별 전문 에이전트 분석
   - AssemblyBinaryAgent (어셈블리/바이너리)
   - SourceCodeAgent (소스 코드)
   - LogsConfigAgent (로그/설정)
   ↓
4. AI Orchestrator가 종합 피드백 생성
   - 모든 에이전트 결과 통합
   - 상세 보안 분석 리포트 작성 (마크다운 형식)
   ↓
5. DB에 종합 피드백 저장
   - POST /files/{file_id}/llm_analysis/
   ↓
6. 프론트엔드에 응답
   - success: true
   - file_id, scan_id
   - analysis_preview (처음 500자)
```

---

## 🔧 추가 API 엔드포인트

### 2. 파일 업로드 분석

**엔드포인트**: `POST /api/v1/analyze`

**설명**: 파일을 직접 업로드하여 분석합니다. (DB 없이 사용 가능)

#### 요청

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze" \
  -F "file=@your_file.py"
```

#### 응답

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "파일 분석 요청이 성공적으로 접수되었습니다. 백그라운드에서 분석이 진행됩니다."
}
```

---

### 3. 분석 결과 조회

**엔드포인트**: `GET /api/v1/report/{task_id}`

**설명**: 업로드한 파일의 분석 결과를 조회합니다.

#### 요청

```bash
curl "http://127.0.0.1:8000/api/v1/report/550e8400-e29b-41d4-a716-446655440000"
```

#### 응답

```json
{
  "file_name": "test.py",
  "file_type": "source_code",
  "is_pqc_vulnerable": true,
  "vulnerability_details": "RSA-2048 암호화 사용이 감지되었습니다.",
  "detected_algorithms": ["RSA-2048", "SHA-256"],
  "recommendations": "RSA를 Kyber로 교체하세요.",
  "evidence": "from Crypto.PublicKey import RSA",
  "confidence_score": 0.95
}
```

---

### 4. 에이전트별 직접 분석 (벤치마크/테스트용)

#### 4.1 Source Code Agent

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/source_code" \
  -F "file=@code.py"
```

#### 4.2 Assembly/Binary Agent

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/assembly_binary" \
  -F "file=@binary.asm"
```

#### 4.3 Logs/Config Agent

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/logs_config" \
  -F "file=@server.log"
```

---

## 📊 DB 스키마 (참고용)

### 저장되는 데이터

#### 1. LLM Assembly (어셈블리 파일)
- **테이블**: `LLM`
- **필드**: `File_id`, `Scan_id`, `Field_text`

#### 2. LLM Code (생성된 코드)
- **테이블**: `LLM`
- **필드**: `File_id`, `Scan_id`, `Code`

#### 3. LLM Log (로그)
- **테이블**: `LLM`
- **필드**: `File_id`, `Scan_id`, `Log`

#### 4. LLM Analysis (종합 분석 결과)
- **테이블**: `LLM_Analysis` (또는 LLM 테이블)
- **필드**: `File_id`, `Scan_id`, `LLM_analysis`
- **형식**: 마크다운 형식의 종합 보안 분석 리포트

---

## 🌐 프론트엔드 통합 예시

### JavaScript (Fetch API)

```javascript
// DB 기반 분석 요청
async function analyzeFromDB(fileId, scanId) {
  const response = await fetch(
    `https://your-ngrok-url.ngrok-free.app/api/v1/analyze/db?file_id=${fileId}&scan_id=${scanId}`,
    {
      method: 'POST'
    }
  );

  const data = await response.json();

  if (data.message) {
    console.log('✅ 분석 성공!');
    console.log(`File ID: ${data.file_id}`);
    console.log(`Scan ID: ${data.scan_id}`);
    console.log(`미리보기:\n${data.analysis_preview}`);
  } else {
    console.error('❌ 분석 실패:', data.detail);
  }

  return data;
}

// 사용 예시
analyzeFromDB(1, 1);
```

### React 예시

```jsx
import React, { useState } from 'react';

function AnalysisComponent() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const analyzeFile = async (fileId, scanId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `https://your-ngrok-url.ngrok-free.app/api/v1/analyze/db?file_id=${fileId}&scan_id=${scanId}`,
        { method: 'POST' }
      );

      const data = await response.json();

      if (data.message) {
        setResult(data);
      } else {
        setError(data.detail);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => analyzeFile(1, 1)} disabled={loading}>
        {loading ? '분석 중...' : '분석 시작'}
      </button>

      {result && (
        <div>
          <h3>✅ 분석 완료</h3>
          <p>File ID: {result.file_id}</p>
          <p>Scan ID: {result.scan_id}</p>
          <pre>{result.analysis_preview}</pre>
        </div>
      )}

      {error && <div style={{color: 'red'}}>❌ {error}</div>}
    </div>
  );
}
```

### Python 예시

```python
import requests

def analyze_from_db(file_id: int, scan_id: int):
    url = f"https://your-ngrok-url.ngrok-free.app/api/v1/analyze/db"
    params = {"file_id": file_id, "scan_id": scan_id}

    response = requests.post(url, params=params)
    data = response.json()

    if "message" in data:
        print("✅ 분석 성공!")
        print(f"File ID: {data['file_id']}")
        print(f"Scan ID: {data['scan_id']}")
        print(f"\n미리보기:\n{data['analysis_preview']}")
    else:
        print(f"❌ 분석 실패: {data.get('detail')}")

    return data

# 사용
result = analyze_from_db(1, 1)
```

---

## 🔐 에러 핸들링

### 가능한 에러 코드

| 상태 코드 | 설명 | 해결 방법 |
|----------|------|----------|
| 200 | 성공 | - |
| 400 | 잘못된 요청 (DB에 데이터 없음) | file_id와 scan_id 확인 |
| 404 | 리소스 없음 | 엔드포인트 URL 확인 |
| 422 | 유효성 검사 실패 | 파라미터 타입 확인 |
| 500 | 서버 내부 오류 | 서버 로그 확인 |

---

## 📝 응답 데이터 구조

### 성공 응답

```typescript
interface AnalysisResponse {
  message: string;              // "분석이 성공적으로 완료되었습니다."
  file_id: number;              // 분석한 파일 ID
  scan_id: number;              // 스캔 세션 ID
  analysis_preview: string;     // 종합 분석 결과 미리보기 (500자)
}
```

### 실패 응답

```typescript
interface ErrorResponse {
  detail: string;               // 오류 메시지
}
```

---

## 🚀 API 테스트

### Swagger UI (추천)

브라우저에서 접속:
```
http://127.0.0.1:8000/docs
```

또는 ngrok URL:
```
https://your-ngrok-url.ngrok-free.app/docs
```

대화형 API 문서에서 직접 테스트 가능합니다.

### curl로 빠른 테스트

```bash
# 1. 서버 상태 확인
curl http://127.0.0.1:8000/

# 2. DB 분석 실행
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db?file_id=1&scan_id=1"

# 3. 결과 확인 (DB 팀에 문의)
```

---

## 💡 중요 참고사항

### 1. DB GET 엔드포인트 상태
현재 DB API의 GET 메서드가 일시적으로 작동하지 않을 수 있습니다.
- DB 팀에서 GET 메서드를 활성화할 때까지 대기
- 활성화되면 `/api/v1/analyze/db` API가 정상 작동

### 2. 필수 조건
분석 전에 DB에 다음 데이터가 있어야 합니다:
- FileScan 레코드 (file_id, scan_id)
- 어셈블리 파일 (`POST /files/{file_id}/llm/`)
- 또는 코드 파일 (`POST /files/{file_id}/llm_code/`)
- 또는 로그 파일 (`POST /files/{file_id}/llm_log/`)

최소 1개 이상의 파일이 있어야 분석이 가능합니다.

### 3. 분석 시간
- 파일 크기와 복잡도에 따라 10초 ~ 2분 소요
- 백그라운드에서 처리되므로 응답은 즉시 반환

### 4. Rate Limiting
ngrok 무료 플랜 사용 시:
- 분당 40개 요청 제한
- 초과 시 429 에러 발생

---

## 📞 문의

- **AI Server 이슈**: GitHub Issues
- **DB API 문의**: DB 팀
- **ngrok URL**: `.ngrok_url` 파일 확인

---

**업데이트 날짜**: 2025-11-18
**API 버전**: v1
