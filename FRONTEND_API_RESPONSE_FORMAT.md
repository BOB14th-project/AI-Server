# 프런트엔드 API 응답 포맷 가이드

**테스트 일시**: 2025-11-20
**서버 버전**: PQC Inspector AI Server v1.0
**Base URL**: `http://127.0.0.1:8000`

---

## 📋 목차

1. [개별 파일 분석 API](#1-개별-파일-분석-api)
2. [전체 파일 일괄 분석 API](#2-전체-파일-일괄-분석-api)
3. [응답 구조 상세 설명](#3-응답-구조-상세-설명)
4. [프런트엔드 통합 예제](#4-프런트엔드-통합-예제)
5. [에러 응답 처리](#5-에러-응답-처리)

---

## 1. 개별 파일 분석 API

### 엔드포인트
```
POST /api/v1/analyze/db?file_id={file_id}&scan_id={scan_id}
```

### 요청 파라미터
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `file_id` | integer | ✅ | 분석할 파일의 ID |
| `scan_id` | integer | ✅ | 스캔 세션 ID |

### 요청 예시
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db?file_id=1&scan_id=1"
```

### 성공 응답 (HTTP 200)

```json
{
  "message": "분석이 성공적으로 완료되었습니다.",
  "file_id": 1,
  "scan_id": 1,
  "analysis_preview": "---\n# 1. 스캔 대상\n\n**File ID**: 1  \n**Scan ID**: 1\n\n## 1.1 파일 정보\n- **분석 대상 파일**: dump.5b43b3dcb9a6cd57.asm\n- **파일 타입**: 어셈블리\n- **파일 크기**: 147244 bytes\n- **분석 일시**: 2024-06-14  (UTC 기준)\n\n## 1.2 검사 범위\n- **검사한 암호 알고리즘**: (탐지된 알고리즘 없음, 암호화 관련 문자열만 존재)\n- **분석 레벨**: 어셈블리\n- **사용된 AI 에이전트**: assembly_binary\n\n## 1.3 전체 요약\n- **보안 상태**: 주의\n- **PQC 취약점 발견**: 예 (잠재적)\n- **위험도 등급**: Medium\n- **종합 신뢰도**: 0.3\n\n---\n\n# 2. 상세 내용\n\n## 2.1 발견된 취약점\n\n### 취약점 #1: 잠재적 비양자내성 암호 사용\n- **심각도**: Medium\n- **발견 위치**: 어셈블리\n- **탐지 근거**: ...\n\n## 2.2 기술적 분석\n...\n\n## 2.3 종합 평가\n...\n\n---\n\n# 3. 전환 가이드\n\n## 3.1 즉시 조치 필요 사항\n...\n\n## 3.2 양자내성 암호 전환 로드맵\n...\n\n## 3.3 권장 라이브러리 및 도구\n...\n\n## 3.4 추가 리소스\n..."
}
```

### 응답 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `message` | string | 작업 완료 메시지 |
| `file_id` | integer | 분석된 파일 ID |
| `scan_id` | integer | 스캔 세션 ID |
| `analysis_preview` | string | **마크다운 형식의 종합 보안 리포트** (전체 내용) |

### `analysis_preview` 구조

`analysis_preview`는 **마크다운 형식**의 문자열로, 다음 3개 섹션으로 구성됩니다:

#### 📌 섹션 1: 스캔 대상
```markdown
# 1. 스캔 대상

**File ID**: 1
**Scan ID**: 1

## 1.1 파일 정보
- **분석 대상 파일**: dump.5b43b3dcb9a6cd57.asm
- **파일 타입**: 어셈블리
- **파일 크기**: 147244 bytes
- **분석 일시**: 2024-06-14 (UTC 기준)

## 1.2 검사 범위
- **검사한 암호 알고리즘**: ...
- **분석 레벨**: 어셈블리
- **사용된 AI 에이전트**: assembly_binary

## 1.3 전체 요약
- **보안 상태**: 주의
- **PQC 취약점 발견**: 예 (잠재적)
- **위험도 등급**: Medium
- **종합 신뢰도**: 0.3
```

#### 📌 섹션 2: 상세 내용
```markdown
# 2. 상세 내용

## 2.1 발견된 취약점

### 취약점 #1: 잠재적 비양자내성 암호 사용
- **심각도**: Medium
- **발견 위치**: 어셈블리
- **탐지 근거**: ...
- **양자컴퓨터 위협**: ...
- **예상 피해**: ...

## 2.2 기술적 분석

### 어셈블리 레벨 분석
- **분석 결과**: ...
- **암호 함수 호출**: ...
- **코드 패턴**: ...

### 소스코드 레벨 분석
- **분석 결과**: ...

### 로그/설정 분석
- **분석 결과**: ...

## 2.3 종합 평가
- **전반적 보안 수준**: ...
- **주요 위험 요소**: ...
- **긍정적 요소**: ...
```

#### 📌 섹션 3: 전환 가이드
```markdown
# 3. 전환 가이드

## 3.1 즉시 조치 필요 사항 (High Priority)
1. **RSA-2048 키 교환 프로토콜 개선**
   - 현재: RSA-2048 키 교환
   - 조치: 하이브리드 방식 도입 (RSA-2048 + CRYSTALS-Kyber)
   - 예상 기간: 1-2개월

## 3.2 양자내성 암호 전환 로드맵

### 단기 계획 (1-3개월)
- ...

### 중기 계획 (3-6개월)
- ...

### 장기 계획 (6-12개월)
- ...

## 3.3 권장 라이브러리 및 도구
- **NIST PQC 표준 라이브러리**: liboqs 0.9.0+, PQClean
- **호환성 도구**: OQS-OpenSSL 1.1.1
- **모니터링 도구**: PQC Inspector

## 3.4 추가 리소스
- **NIST PQC 프로젝트**: https://csrc.nist.gov/projects/post-quantum-cryptography
- **마이그레이션 가이드**: NIST SP 800-208
```

---

## 2. 전체 파일 일괄 분석 API

### 엔드포인트
```
POST /api/v1/analyze/db/all?scan_id={scan_id}&max_files={max_files}
```

### 요청 파라미터
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `scan_id` | integer | ✅ | - | 스캔 세션 ID |
| `max_files` | integer | ❌ | 100 | 최대 검사할 파일 개수 |

### 요청 예시
```bash
# 모든 파일 검사 (최대 100개)
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db/all?scan_id=1"

# 최대 3개 파일만 검사
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db/all?scan_id=1&max_files=3"
```

### 성공 응답 (HTTP 200)

```json
{
  "message": "전체 파일 분석이 완료되었습니다.",
  "scan_id": 1,
  "total_attempted": 2,
  "total_success": 2,
  "total_failed": 0,
  "results": [
    {
      "file_id": 1,
      "status": "success",
      "message": "분석 완료"
    },
    {
      "file_id": 3,
      "status": "success",
      "message": "분석 완료"
    }
  ]
}
```

### 응답 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `message` | string | 작업 완료 메시지 |
| `scan_id` | integer | 스캔 세션 ID |
| `total_attempted` | integer | 시도한 총 파일 개수 |
| `total_success` | integer | 성공한 파일 개수 |
| `total_failed` | integer | 실패한 파일 개수 |
| `results` | array | 각 파일의 분석 결과 배열 |

### `results` 배열 항목

| 필드 | 타입 | 설명 |
|------|------|------|
| `file_id` | integer | 파일 ID |
| `status` | string | `"success"` 또는 `"failed"` |
| `message` | string | 성공 시: "분석 완료" |
| `error` | string | 실패 시에만 포함: 에러 메시지 |

### 실패 케이스 예시

```json
{
  "message": "전체 파일 분석이 완료되었습니다.",
  "scan_id": 1,
  "total_attempted": 5,
  "total_success": 3,
  "total_failed": 2,
  "results": [
    {
      "file_id": 1,
      "status": "success",
      "message": "분석 완료"
    },
    {
      "file_id": 2,
      "status": "success",
      "message": "분석 완료"
    },
    {
      "file_id": 3,
      "status": "success",
      "message": "분석 완료"
    },
    {
      "file_id": 4,
      "status": "failed",
      "error": "DB에 분석할 데이터가 없습니다."
    },
    {
      "file_id": 5,
      "status": "failed",
      "error": "AI 분석 중 오류가 발생했습니다."
    }
  ]
}
```

---

## 3. 응답 구조 상세 설명

### 개별 파일 분석 응답 구조

```typescript
interface IndividualAnalysisResponse {
  message: string;              // "분석이 성공적으로 완료되었습니다."
  file_id: number;              // 분석된 파일 ID
  scan_id: number;              // 스캔 세션 ID
  analysis_preview: string;     // 마크다운 형식의 종합 보안 리포트
}
```

### 전체 파일 일괄 분석 응답 구조

```typescript
interface BatchAnalysisResponse {
  message: string;              // "전체 파일 분석이 완료되었습니다."
  scan_id: number;              // 스캔 세션 ID
  total_attempted: number;      // 시도한 총 파일 개수
  total_success: number;        // 성공한 파일 개수
  total_failed: number;         // 실패한 파일 개수
  results: AnalysisResult[];    // 각 파일의 분석 결과 배열
}

interface AnalysisResult {
  file_id: number;              // 파일 ID
  status: "success" | "failed"; // 분석 상태
  message?: string;             // 성공 시 메시지
  error?: string;               // 실패 시 에러 메시지
}
```

---

## 4. 프런트엔드 통합 예제

### React + TypeScript 예제

#### 4.1 타입 정의

```typescript
// types/api.ts

export interface IndividualAnalysisResponse {
  message: string;
  file_id: number;
  scan_id: number;
  analysis_preview: string;
}

export interface BatchAnalysisResponse {
  message: string;
  scan_id: number;
  total_attempted: number;
  total_success: number;
  total_failed: number;
  results: AnalysisResult[];
}

export interface AnalysisResult {
  file_id: number;
  status: "success" | "failed";
  message?: string;
  error?: string;
}

export interface ParsedReport {
  scanTarget: string;    // 섹션 1: 스캔 대상
  details: string;       // 섹션 2: 상세 내용
  migrationGuide: string; // 섹션 3: 전환 가이드
}
```

#### 4.2 API 클라이언트

```typescript
// services/apiClient.ts

const API_BASE_URL = "http://127.0.0.1:8000";

export class PQCInspectorAPI {
  // 개별 파일 분석
  static async analyzeFile(
    fileId: number,
    scanId: number
  ): Promise<IndividualAnalysisResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/analyze/db?file_id=${fileId}&scan_id=${scanId}`,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // 전체 파일 일괄 분석
  static async analyzeAllFiles(
    scanId: number,
    maxFiles: number = 100
  ): Promise<BatchAnalysisResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/analyze/db/all?scan_id=${scanId}&max_files=${maxFiles}`,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }
}
```

#### 4.3 마크다운 파싱 유틸리티

```typescript
// utils/reportParser.ts

export function parseReport(markdown: string): ParsedReport {
  const sections: ParsedReport = {
    scanTarget: "",
    details: "",
    migrationGuide: "",
  };

  // 섹션 1: 스캔 대상
  const scanMatch = markdown.match(
    /# 1\. 스캔 대상([\s\S]*?)(?=# 2\. 상세 내용|$)/
  );
  sections.scanTarget = scanMatch ? scanMatch[1].trim() : "";

  // 섹션 2: 상세 내용
  const detailsMatch = markdown.match(
    /# 2\. 상세 내용([\s\S]*?)(?=# 3\. 전환 가이드|$)/
  );
  sections.details = detailsMatch ? detailsMatch[1].trim() : "";

  // 섹션 3: 전환 가이드
  const guideMatch = markdown.match(/# 3\. 전환 가이드([\s\S]*?)$/);
  sections.migrationGuide = guideMatch ? guideMatch[1].trim() : "";

  return sections;
}
```

#### 4.4 React 컴포넌트

```tsx
// components/FileAnalysis.tsx

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { PQCInspectorAPI } from "../services/apiClient";
import { parseReport } from "../utils/reportParser";
import type { IndividualAnalysisResponse } from "../types/api";

export function FileAnalysis() {
  const [fileId, setFileId] = useState<number>(1);
  const [scanId, setScanId] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<IndividualAnalysisResponse | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const result = await PQCInspectorAPI.analyzeFile(fileId, scanId);
      setResponse(result);
    } catch (error) {
      console.error("분석 실패:", error);
      alert("분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const sections = response ? parseReport(response.analysis_preview) : null;

  return (
    <div className="file-analysis">
      <h1>파일 분석</h1>

      <div className="input-section">
        <label>
          File ID:
          <input
            type="number"
            value={fileId}
            onChange={(e) => setFileId(Number(e.target.value))}
          />
        </label>

        <label>
          Scan ID:
          <input
            type="number"
            value={scanId}
            onChange={(e) => setScanId(Number(e.target.value))}
          />
        </label>

        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? "분석 중..." : "분석 시작"}
        </button>
      </div>

      {response && sections && (
        <div className="results">
          <div className="message">{response.message}</div>

          <div className="tabs">
            <div className="tab-panel">
              <h2>1. 스캔 대상</h2>
              <ReactMarkdown>{sections.scanTarget}</ReactMarkdown>
            </div>

            <div className="tab-panel">
              <h2>2. 상세 내용</h2>
              <ReactMarkdown>{sections.details}</ReactMarkdown>
            </div>

            <div className="tab-panel">
              <h2>3. 전환 가이드</h2>
              <ReactMarkdown>{sections.migrationGuide}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 4.5 일괄 분석 컴포넌트

```tsx
// components/BatchAnalysis.tsx

import React, { useState } from "react";
import { PQCInspectorAPI } from "../services/apiClient";
import type { BatchAnalysisResponse } from "../types/api";

export function BatchAnalysis() {
  const [scanId, setScanId] = useState<number>(1);
  const [maxFiles, setMaxFiles] = useState<number>(10);
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<BatchAnalysisResponse | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const result = await PQCInspectorAPI.analyzeAllFiles(scanId, maxFiles);
      setResponse(result);
    } catch (error) {
      console.error("일괄 분석 실패:", error);
      alert("일괄 분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="batch-analysis">
      <h1>전체 파일 일괄 분석</h1>

      <div className="input-section">
        <label>
          Scan ID:
          <input
            type="number"
            value={scanId}
            onChange={(e) => setScanId(Number(e.target.value))}
          />
        </label>

        <label>
          최대 파일 수:
          <input
            type="number"
            value={maxFiles}
            onChange={(e) => setMaxFiles(Number(e.target.value))}
          />
        </label>

        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? "분석 중..." : "일괄 분석 시작"}
        </button>
      </div>

      {response && (
        <div className="results">
          <h2>{response.message}</h2>

          <div className="summary">
            <p>총 시도: {response.total_attempted}</p>
            <p>성공: {response.total_success}</p>
            <p>실패: {response.total_failed}</p>
          </div>

          <table>
            <thead>
              <tr>
                <th>File ID</th>
                <th>상태</th>
                <th>메시지</th>
              </tr>
            </thead>
            <tbody>
              {response.results.map((result) => (
                <tr key={result.file_id}>
                  <td>{result.file_id}</td>
                  <td>
                    <span className={`status-${result.status}`}>
                      {result.status === "success" ? "✅ 성공" : "❌ 실패"}
                    </span>
                  </td>
                  <td>{result.message || result.error}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
```

### Vanilla JavaScript 예제

```javascript
// 개별 파일 분석
async function analyzeFile(fileId, scanId) {
  const response = await fetch(
    `http://127.0.0.1:8000/api/v1/analyze/db?file_id=${fileId}&scan_id=${scanId}`,
    { method: 'POST' }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// 전체 파일 일괄 분석
async function analyzeAllFiles(scanId, maxFiles = 100) {
  const response = await fetch(
    `http://127.0.0.1:8000/api/v1/analyze/db/all?scan_id=${scanId}&max_files=${maxFiles}`,
    { method: 'POST' }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// 마크다운 파싱
function parseReport(markdown) {
  const sections = {};

  // 섹션 1: 스캔 대상
  const scanMatch = markdown.match(/# 1\. 스캔 대상([\s\S]*?)(?=# 2\. 상세 내용)/);
  sections.scanTarget = scanMatch ? scanMatch[1].trim() : '';

  // 섹션 2: 상세 내용
  const detailsMatch = markdown.match(/# 2\. 상세 내용([\s\S]*?)(?=# 3\. 전환 가이드)/);
  sections.details = detailsMatch ? detailsMatch[1].trim() : '';

  // 섹션 3: 전환 가이드
  const guideMatch = markdown.match(/# 3\. 전환 가이드([\s\S]*?)$/);
  sections.migrationGuide = guideMatch ? guideMatch[1].trim() : '';

  return sections;
}

// 사용 예시
(async () => {
  try {
    // 개별 파일 분석
    const result = await analyzeFile(1, 1);
    console.log('분석 완료:', result.message);
    console.log('File ID:', result.file_id);
    console.log('Scan ID:', result.scan_id);

    // 마크다운 파싱
    const sections = parseReport(result.analysis_preview);
    console.log('스캔 대상:', sections.scanTarget);
    console.log('상세 내용:', sections.details);
    console.log('전환 가이드:', sections.migrationGuide);

  } catch (error) {
    console.error('에러 발생:', error);
  }
})();
```

---

## 5. 에러 응답 처리

### 에러 응답 형식

모든 에러는 FastAPI의 표준 에러 응답 형식을 따릅니다:

```json
{
  "detail": "에러 메시지"
}
```

### 일반적인 에러 케이스

#### 1. 데이터 없음 (HTTP 404)

```json
{
  "detail": "DB에 분석할 데이터가 없습니다."
}
```

**발생 상황**:
- 해당 `file_id`와 `scan_id`에 대한 데이터가 DB에 없을 때
- 파일이 삭제되었거나 아직 업로드되지 않았을 때

#### 2. 파라미터 누락 (HTTP 422)

```json
{
  "detail": [
    {
      "loc": ["query", "file_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**발생 상황**:
- 필수 파라미터(`file_id`, `scan_id`)가 누락되었을 때

#### 3. 서버 내부 오류 (HTTP 500)

```json
{
  "detail": "내부 서버 오류가 발생했습니다."
}
```

**발생 상황**:
- AI 모델 API 호출 실패
- DB 연결 오류
- 예상치 못한 서버 오류

### 프런트엔드 에러 처리 예제

```typescript
async function analyzeFileWithErrorHandling(fileId: number, scanId: number) {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/v1/analyze/db?file_id=${fileId}&scan_id=${scanId}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      const errorData = await response.json();

      // 에러 타입별 처리
      if (response.status === 404) {
        throw new Error('분석할 데이터를 찾을 수 없습니다.');
      } else if (response.status === 422) {
        throw new Error('잘못된 요청 파라미터입니다.');
      } else if (response.status === 500) {
        throw new Error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      } else {
        throw new Error(errorData.detail || '알 수 없는 오류가 발생했습니다.');
      }
    }

    return await response.json();

  } catch (error) {
    console.error('API 호출 실패:', error);
    throw error;
  }
}
```

---

## 6. 실전 테스트 결과

### 테스트 환경
- **서버**: `http://127.0.0.1:8000`
- **테스트 날짜**: 2025-11-20
- **Python 버전**: 3.13
- **FastAPI 버전**: 최신

### 개별 파일 분석 테스트

**요청**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db?file_id=1&scan_id=1"
```

**응답 요약**:
- ✅ HTTP Status: 200
- ✅ 응답 시간: ~41초 (README 기준)
- ✅ `message`: "분석이 성공적으로 완료되었습니다."
- ✅ `file_id`: 1
- ✅ `scan_id`: 1
- ✅ `analysis_preview`: 마크다운 형식 보고서 (3개 섹션 포함)

### 전체 파일 일괄 분석 테스트

**요청**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db/all?scan_id=1&max_files=3"
```

**응답 요약**:
- ✅ HTTP Status: 200
- ✅ `message`: "전체 파일 분석이 완료되었습니다."
- ✅ `scan_id`: 1
- ✅ `total_attempted`: 2 (file_id 1, 3 존재, file_id 2 없음)
- ✅ `total_success`: 2
- ✅ `total_failed`: 0
- ✅ `results`: 각 파일의 분석 상태 포함

---

## 7. 주의사항 및 권장사항

### 성능 고려사항

1. **분석 시간**
   - 개별 파일: 평균 41초 (README 기준)
   - 일괄 분석: 파일 개수 × 41초
   - 프런트엔드에서 **로딩 UI** 필수

2. **API 타임아웃 설정**
   ```javascript
   // 최소 60초 이상 권장
   const controller = new AbortController();
   const timeoutId = setTimeout(() => controller.abort(), 120000); // 2분

   fetch(url, {
     method: 'POST',
     signal: controller.signal
   });
   ```

3. **일괄 분석 시 `max_files` 제한**
   - 권장값: 10개 이하
   - 이유: 과도한 분석 시간 방지

### 데이터 처리

1. **마크다운 렌더링**
   - 추천 라이브러리: `react-markdown`, `marked`, `showdown`
   - 보안: XSS 방지를 위해 sanitize 옵션 활성화

2. **긴 리포트 처리**
   - `analysis_preview`는 수 KB 크기 가능
   - 필요시 가상 스크롤링 또는 페이지네이션 적용

3. **캐싱 전략**
   - 동일한 `file_id` + `scan_id` 조합은 캐시 활용
   - 브라우저 `localStorage` 또는 `sessionStorage` 활용 가능

### 보안

1. **API 키 관리**
   - 프로덕션 환경에서는 환경 변수로 관리
   - `.env` 파일은 절대 커밋하지 말 것

2. **CORS 설정**
   - 현재 서버는 모든 origin 허용 (개발 환경)
   - 프로덕션에서는 특정 도메인만 허용하도록 설정 필요

3. **입력 검증**
   - `file_id`, `scan_id`는 양의 정수만 허용
   - 프런트엔드에서 1차 검증 후 API 호출

---

## 8. 추가 리소스

### 관련 문서
- **README.md**: 전체 시스템 아키텍처 및 설치 가이드
- **REPORT_FORMAT_SAMPLE.md**: 보고서 샘플
- **db_api_docs.txt**: 백엔드 DB API 문서

### API 문서
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 예제 코드
- 위 섹션의 React + TypeScript 예제
- Vanilla JavaScript 예제

---

**문서 작성**: 2025-11-20
**마지막 업데이트**: 2025-11-20
**작성자**: PQC Inspector Team
