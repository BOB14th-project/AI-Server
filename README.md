# 🛡️ PQC Inspector AI Server

**양자내성암호(PQC) 전환을 위한 AI 기반 보안 분석 시스템**

바이너리, 소스코드, 로그 파일에서 비양자내성암호(Non-PQC) 사용을 자동으로 탐지하고 **3개 카테고리 종합 보안 리포트**를 생성하는 AI 서버입니다.

---

## ✨ 주요 기능

### 🧠 AI 기반 다중 에이전트 분석 시스템
- **지능형 파일 분류**: GPT-4o-mini가 파일 타입을 자동 분류
- **전문 에이전트**: 각 파일 타입별로 특화된 AI 에이전트
  - 🔧 **AssemblyBinaryAgent**: 바이너리 디스어셈블 + 어셈블리 코드 분석 (Capstone + Gemini 2.0 Flash)
  - 💻 **SourceCodeAgent**: 소스코드 분석 (Gemini 2.0 Flash)
  - 📝 **LogsConfigAgent**: 로그/설정 파일 분석 (Gemini 2.0 Flash)
- **종합 리포트 생성**: GPT-4o-mini가 모든 에이전트 결과를 통합하여 **3개 카테고리 보고서** 작성

### 📋 3개 카테고리 구조화 보고서 (신규!)
프론트엔드에서 파싱하기 쉽도록 명확한 구조로 생성:
1. **# 1. 스캔 대상** - 파일 정보, 검사 범위, 전체 요약
2. **# 2. 상세 내용** - 발견된 취약점, 기술 분석, 종합 평가
3. **# 3. 전환 가이드** - 즉시 조치사항, PQC 로드맵, 권장 도구

### 🔧 Capstone 기반 바이너리 전처리
- **자동 디스어셈블**: 바이너리 파일을 x86/x64 어셈블리로 자동 변환
- **지능형 필터링**: 암호화 관련 코드만 추출 (70+ 키워드 패턴 매칭)
- **컨텍스트 최적화**: 1.7MB 바이너리 → 2.5KB로 축약 (99.85% 축소)
- **OpenSSL 함수 탐지**: RSA_new, EVP_PKEY_keygen 등 자동 인식

### 📚 RAG (Retrieval-Augmented Generation) 강화
- **벡터 데이터베이스**: ChromaDB를 활용한 고속 유사도 검색
- **전문 지식 베이스**: 에이전트별 특화된 암호화 패턴 데이터베이스
- **실시간 컨텍스트 검색**: 분석 중 관련 전문 지식 자동 검색

### 💾 외부 DB 완전 통합
- **개별 파일 분석**: file_id + scan_id로 특정 파일 분석
- **전체 파일 일괄 분석** (신규!): scan_id만으로 DB의 모든 파일 자동 검사
- **종합 보고서 저장**: 분석 결과를 DB에 마크다운 형식으로 저장
- **프론트엔드 친화적**: RESTful API 설계

---

## 🏗️ 시스템 아키텍처

```
┌─────────────┐
│ 프론트엔드   │
│ (React 등)  │
└─────┬───────┘
      │ POST /api/v1/analyze/db/all?scan_id=1 (전체 파일)
      │ POST /api/v1/analyze/db?file_id=1&scan_id=1 (개별 파일)
      │
      ▼
┌─────────────────────────────────────────────────────┐
│                  AI Server (FastAPI)                │
├─────────────────────────────────────────────────────┤
│  1️⃣ DB에서 데이터 조회                               │
│     ├─ 어셈블리/바이너리 (GET /files/.../llm/)      │
│     ├─ 소스코드 (GET /files/.../llm_code/)         │
│     └─ 로그 (GET /files/.../llm_log/)              │
│                                                     │
│  2️⃣ Capstone 바이너리 전처리                         │
│     ├─ 디스어셈블: 바이너리 → 어셈블리               │
│     ├─ 패턴 필터링: 암호화 관련 코드만 추출          │
│     └─ 컨텍스트 축약: LLM 입력 크기 최적화           │
│                                                     │
│  3️⃣ AI 에이전트 병렬 분석                            │
│     ├─ AssemblyBinaryAgent (Gemini 2.0 Flash)      │
│     ├─ SourceCodeAgent (Gemini 2.0 Flash)          │
│     └─ LogsConfigAgent (Gemini 2.0 Flash)          │
│     │                                               │
│     └─ RAG 강화 (ChromaDB 벡터 검색)                │
│                                                     │
│  4️⃣ AI Orchestrator 종합 분석 (GPT-4o-mini)         │
│     └─ 3개 카테고리 마크다운 보안 리포트 생성        │
│                                                     │
│  5️⃣ DB에 종합 보고서 저장                            │
│     └─ POST /files/.../llm_analysis/               │
└─────┬───────────────────────────────────────────────┘
      │
      ▼
┌─────────────┐
│  외부 DB    │
│ (Backend)   │
└─────────────┘
```

---

## 🚀 빠른 시작

### 📋 사전 준비

- **Python 3.9+**
- **API 키**:
  - OpenAI API 키 (GPT-4o-mini, text-embedding-3-small)
  - Google API 키 (Gemini 2.0 Flash)
- **외부 DB Backend API** (파일 데이터 조회용)
- **ngrok** (외부 접근용, 선택사항)

### 1️⃣ 설치

```bash
# 프로젝트 클론
git clone <repository-url>
cd AI-Server

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ 환경 변수 설정

`.env` 파일 생성:

```bash
# AI API 키
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# 외부 DB API 설정
EXTERNAL_API_BASE_URL=https://your-backend-api.ngrok-free.dev

# AI 모델 설정 (선택사항)
ORCHESTRATOR_MODEL=gpt-4.1
SOURCE_CODE_MODEL=gemini-2.0-flash
BINARY_MODEL=gemini-2.0-flash
LOG_CONF_MODEL=gemini-2.0-flash

# 서버 설정
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
LOG_LEVEL=INFO
```

### 3️⃣ 서버 실행

```bash
# 로컬 실행
python main.py

# 서버 확인
curl http://127.0.0.1:8000/
# {"message":"PQC Inspector 서버가 정상적으로 실행 중입니다!"}
```

### 4️⃣ ngrok으로 외부 접근 (선택사항)

```bash
# ngrok 설치 (https://ngrok.com/download)
# 계정 생성 후 authtoken 설정

# 터널 시작
ngrok http 8000

# 출력된 URL 예시:
# Forwarding: https://abc123.ngrok-free.app -> http://localhost:8000
```

**ngrok URL을 프론트엔드에 공유**하면 어디서든 접근 가능합니다.

---

## 📡 API 엔드포인트

### Base URL

**로컬**: `http://127.0.0.1:8000`
**ngrok**: `https://your-ngrok-url.ngrok-free.app`

### 핵심 엔드포인트

#### 1. 서버 상태 확인

```bash
GET /
```

**응답**:
```json
{"message":"PQC Inspector 서버가 정상적으로 실행 중입니다!"}
```

---

#### 2. 전체 파일 일괄 분석 ⭐️ (신규!)

```bash
POST /api/v1/analyze/db/all?scan_id={scan_id}&max_files={max_files}
```

**설명**: DB에 있는 모든 파일을 자동으로 검사합니다 (file_id 1부터 순회)

**요청 파라미터**:
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `scan_id` | integer | ✅ | - | 스캔 세션 ID |
| `max_files` | integer | ❌ | 100 | 최대 검사할 파일 개수 |

**요청 예시**:
```bash
# 모든 파일 검사 (최대 100개)
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db/all?scan_id=1"

# 최대 10개 파일만 검사
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db/all?scan_id=1&max_files=10"
```

**성공 응답**:
```json
{
  "message": "전체 파일 분석이 완료되었습니다.",
  "scan_id": 1,
  "total_attempted": 5,
  "total_success": 3,
  "total_failed": 2,
  "results": [
    {"file_id": 1, "status": "success", "message": "분석 완료"},
    {"file_id": 2, "status": "success", "message": "분석 완료"},
    {"file_id": 3, "status": "success", "message": "분석 완료"},
    {"file_id": 5, "status": "failed", "error": "DB에 분석할 데이터가 없습니다."}
  ]
}
```

**프로세스**:
```
1. file_id 1부터 max_files까지 순회
   ↓
2. 각 파일마다 개별 분석 수행
   ↓
3. 데이터 없는 파일은 자동으로 건너뜀
   ↓
4. 성공/실패 통계 집계
```

---

#### 3. 개별 파일 분석 ⭐️

```bash
POST /api/v1/analyze/db?file_id={file_id}&scan_id={scan_id}
```

**설명**: DB에서 특정 파일 데이터를 자동으로 조회 → AI 분석 → 종합 보고서 생성 → DB 저장

**요청 파라미터**:
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `file_id` | integer | 분석할 파일의 ID |
| `scan_id` | integer | 스캔 세션 ID |

**요청 예시**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db?file_id=1&scan_id=1"
```

**성공 응답**:
```json
{
  "message": "분석이 성공적으로 완료되었습니다.",
  "file_id": 1,
  "scan_id": 1,
  "analysis_preview": "# 1. 스캔 대상\n\n**File ID**: 1\n**Scan ID**: 1\n\n## 1.1 파일 정보\n- **분석 대상 파일**: weakcrypto_win.exe..."
}
```

**실패 응답**:
```json
{
  "detail": "DB에 분석할 데이터가 없습니다."
}
```

**프로세스**:
```
1. DB 조회 (어셈블리, 코드, 로그)
   ↓
2. Capstone 바이너리 전처리 (디스어셈블 + 필터링)
   ↓
3. 각 에이전트 병렬 분석 (RAG 강화)
   ↓
4. AI Orchestrator 종합 분석 (3개 카테고리 보고서 생성)
   ↓
5. DB에 마크다운 리포트 저장 (POST /files/{file_id}/llm_analysis/)
   ↓
6. 프론트엔드에 응답 반환
```

---

#### 4. 분석 결과 조회 (DB에서)

**백엔드 DB API 사용**:
```bash
GET https://your-backend-api.ngrok-free.dev/files/{file_id}/llm_analysis/?scan_id={scan_id}
```

**응답**:
```json
[
  {
    "File_id": 1,
    "Scan_id": 1,
    "LLM_analysis": "# 1. 스캔 대상\n\n**File ID**: 1\n**Scan ID**: 1\n\n## 1.1 파일 정보...",
    "created_at": "2025-11-19T06:27:11Z"
  }
]
```

---

#### 5. 파일 업로드 분석 (테스트용)

```bash
POST /api/v1/analyze
Content-Type: multipart/form-data
```

**요청**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze" \
  -F "file=@your_file.py"
```

**응답**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "파일 분석 요청이 성공적으로 접수되었습니다."
}
```

---

#### 6. 에이전트별 직접 분석 (벤치마크용)

**Source Code Agent**:
```bash
POST /api/v1/analyze/source_code
```

**Assembly/Binary Agent**:
```bash
POST /api/v1/analyze/assembly_binary
```

**Logs/Config Agent**:
```bash
POST /api/v1/analyze/logs_config
```

**예시**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/assembly_binary" \
  -F "file=@test_binary"
```

**응답**:
```json
{
  "is_pqc_vulnerable": true,
  "vulnerability_details": "RSA_generate_key_ex@OPENSSL_3.0.0 함수 호출 발견",
  "detected_algorithms": ["RSA"],
  "recommendations": "CRYSTALS-Kyber로 전환 권장",
  "evidence": "RSA_new@OPENSSL_3.0.0, libcrypto.so.3",
  "confidence_score": 0.7
}
```

---

#### 7. API 문서 (Swagger UI)

```bash
http://127.0.0.1:8000/docs
```

브라우저에서 접속하면 모든 API를 인터랙티브하게 테스트할 수 있습니다.

---

## 📄 보고서 형식

### 3개 카테고리 구조

AI Orchestrator가 생성하는 보고서는 프론트엔드에서 파싱하기 쉽도록 명확한 구조를 따릅니다:

```markdown
# 1. 스캔 대상

**File ID**: 1
**Scan ID**: 1

## 1.1 파일 정보
- **분석 대상 파일**: weakcrypto_win.exe
- **파일 타입**: 어셈블리 바이너리 (x86-64)
- **파일 크기**: 147,244 bytes
- **분석 일시**: 2025-11-19 15:27:00 (KST)

## 1.2 검사 범위
- **검사한 암호 알고리즘**: RSA, AES, DES, ECDSA, SHA, MD5
- **분석 레벨**: 어셈블리 레벨 (바이너리 디스어셈블)
- **사용된 AI 에이전트**: AssemblyBinaryAgent

## 1.3 전체 요약
- **보안 상태**: 위험 ⚠️
- **PQC 취약점 발견**: 예
- **위험도 등급**: High
- **종합 신뢰도**: 0.85

---

# 2. 상세 내용

## 2.1 발견된 취약점

### 취약점 #1: RSA-2048
- **심각도**: High
- **발견 위치**: 어셈블리 코드 (OpenSSL 라이브러리 호출)
- **탐지 근거**: RSA_generate_key_ex() 함수 호출 패턴 발견
- **양자컴퓨터 위협**: Shor 알고리즘에 의해 다항 시간 내 인수분해 가능
- **예상 피해**: 암호화된 통신 내용 노출, 전자서명 위조 가능

### 취약점 #2: AES-128
- **심각도**: Medium
- **발견 위치**: 어셈블리 코드
- **탐지 근거**: AES 암호화 루틴 탐지 (128비트 키)
- **양자컴퓨터 위협**: Grover 알고리즘으로 실효 키 길이 64비트로 감소
- **예상 피해**: 양자컴퓨터 환경에서 브루트포스 공격 시간 단축

## 2.2 기술적 분석

### 어셈블리 레벨 분석
- **분석 결과**: OpenSSL libcrypto.so.3 라이브러리 사용 확인
- **암호 함수 호출**: RSA_generate_key_ex@OPENSSL_3.0.0
- **코드 패턴**: 표준 OpenSSL RSA 키 생성 패턴 사용

### 소스코드 레벨 분석
- **분석 결과**: 소스코드 데이터 없음
- **라이브러리 사용**: N/A
- **구현 방식**: N/A

### 로그/설정 분석
- **분석 결과**: 로그 데이터 없음
- **설정 이슈**: N/A
- **로그 패턴**: N/A

## 2.3 종합 평가
- **전반적 보안 수준**: 현재 클래식 컴퓨터 환경에서는 안전하나, 양자컴퓨터 시대에는 취약
- **주요 위험 요소**: RSA-2048 의존도가 높음
- **긍정적 요소**: OpenSSL 최신 버전 사용 (3.0.0)

---

# 3. 전환 가이드

## 3.1 즉시 조치 필요 사항 (High Priority)
1. **RSA-2048 키 교환 프로토콜 개선**
   - 현재: RSA-2048 키 교환
   - 조치: 하이브리드 방식 도입 (RSA-2048 + CRYSTALS-Kyber)
   - 예상 기간: 1-2개월

2. **AES-128 → AES-256 전환**
   - 현재: AES-128 (양자컴퓨터 환경에서 64비트 실효 보안)
   - 조치: AES-256으로 즉시 전환 (128비트 실효 보안 확보)
   - 예상 기간: 1주일

## 3.2 양자내성 암호 전환 로드맵

### 단기 계획 (1-3개월)
1. **현재 암호 → PQC 암호 매핑**
   - RSA-2048 → CRYSTALS-Kyber-768 (키 교환)
   - ECDSA → CRYSTALS-Dilithium-3 (전자서명)
   - AES-128 → AES-256 (대칭키 강화)

2. **마이그레이션 우선순위**
   - [High] 키 교환 프로토콜 (TLS 핸드셰이크)
   - [Medium] 전자서명 검증 시스템
   - [Low] 레거시 API 호환성 유지

### 중기 계획 (3-6개월)
1. **하이브리드 암호 시스템 도입**
   - 기존 RSA + PQC Kyber 병행 운영
   - 점진적 전환을 통한 안정성 확보
   - 상호운용성 테스트 완료

2. **테스트 및 검증**
   - 성능 테스트: TLS 핸드셰이크 시간 측정
   - 호환성 검증: 기존 클라이언트와의 통신 보장
   - 보안 감사: 외부 보안 전문가 리뷰

### 장기 계획 (6-12개월)
1. **완전한 PQC 전환**
   - 모든 레거시 RSA/ECDSA 제거
   - NIST PQC 표준 완전 준수
   - 지속적 모니터링 체계 구축

## 3.3 권장 라이브러리 및 도구
- **NIST PQC 표준 라이브러리**: liboqs 0.9.0+, PQClean, Bouncy Castle PQC
- **호환성 도구**: OQS-OpenSSL 1.1.1, OQS-BoringSSL
- **모니터링 도구**: PQC Inspector, QuantumSafe Scanner

## 3.4 추가 리소스
- **NIST PQC 프로젝트**: https://csrc.nist.gov/projects/post-quantum-cryptography
- **마이그레이션 가이드**: NIST SP 800-208, Open Quantum Safe Wiki
- **기술 지원**: PQC Inspector GitHub Issues
```

### 프론트엔드 파싱 예제

**JavaScript**:
```javascript
// DB에서 리포트 가져오기
const response = await fetch(
  'https://backend-api.ngrok-free.dev/files/1/llm_analysis/?scan_id=1'
);
const data = await response.json();
const reportMarkdown = data[0].LLM_analysis;

// 3개 카테고리 분리
function parseReport(markdown) {
  const sections = {};

  // 1. 스캔 대상
  const scanMatch = markdown.match(/# 1\. 스캔 대상([\s\S]*?)(?=# 2\. 상세 내용)/);
  sections.scanTarget = scanMatch ? scanMatch[1].trim() : '';

  // 2. 상세 내용
  const detailsMatch = markdown.match(/# 2\. 상세 내용([\s\S]*?)(?=# 3\. 전환 가이드)/);
  sections.details = detailsMatch ? detailsMatch[1].trim() : '';

  // 3. 전환 가이드
  const guideMatch = markdown.match(/# 3\. 전환 가이드([\s\S]*?)(?=---\s*\*\*리포트 작성 완료)/);
  sections.migrationGuide = guideMatch ? guideMatch[1].trim() : '';

  return sections;
}

// 사용
const sections = parseReport(reportMarkdown);
```

**React 컴포넌트**:
```jsx
import ReactMarkdown from 'react-markdown';

function SecurityReport({ reportMarkdown }) {
  const sections = parseReport(reportMarkdown);

  return (
    <Tabs>
      <Tab label="스캔 대상">
        <ReactMarkdown>{sections.scanTarget}</ReactMarkdown>
      </Tab>
      <Tab label="상세 내용">
        <ReactMarkdown>{sections.details}</ReactMarkdown>
      </Tab>
      <Tab label="전환 가이드">
        <ReactMarkdown>{sections.migrationGuide}</ReactMarkdown>
      </Tab>
    </Tabs>
  );
}
```

---

## 🔧 Capstone 바이너리 전처리

### 처리 흐름

```
📦 원본 바이너리 파일 (1.7MB)
   ↓
🔍 아키텍처 자동 탐지 (ELF/PE/Mach-O)
   ↓
⚙️ Capstone 디스어셈블 (x86/x64/ARM)
   ↓
🔎 암호화 키워드 필터링 (70+ 패턴)
   ↓
📝 함수 컨텍스트 추출 (±15 instructions)
   ↓
✅ LLM 최적화 결과 (2.5KB, 99.85% 축소)
```

### 지원 아키텍처

- ✅ x86 (32-bit)
- ✅ x86-64 (64-bit)
- ✅ ARM (32-bit, 64-bit)
- ✅ MIPS

### 탐지 패턴 예시

```python
CRYPTO_KEYWORDS = [
    # 클래식 암호
    'rsa', 'aes', 'des', 'ecdsa', 'dsa', 'sha', 'md5',
    # PQC 알고리즘
    'kyber', 'dilithium', 'ntru', 'falcon', 'sphincs',
    # OpenSSL 함수
    'RSA_new', 'EVP_PKEY_keygen', 'BN_set_word',
    # 기타 70+ 패턴...
]
```

---

## 🧪 테스트 워크플로우

### 1. 개별 파일 테스트

```bash
# 1. 서버 실행
python main.py

# 2. 특정 파일 분석 요청
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db?file_id=1&scan_id=1"

# 3. 결과 확인 (DB에서 조회)
curl "https://backend-api.ngrok-free.dev/files/1/llm_analysis/?scan_id=1"
```

### 2. 전체 파일 일괄 테스트

```bash
# 모든 파일 검사 (최대 100개)
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/db/all?scan_id=1"

# 응답:
# {
#   "total_attempted": 5,
#   "total_success": 3,
#   "total_failed": 2,
#   "results": [...]
# }
```

### 3. 성능 측정

**평균 처리 시간** (File ID=1, Scan ID=1 기준):
- DB 조회: ~1초
- Capstone 전처리: ~1초
- AI 에이전트 분석: ~5초
- AI Orchestrator 종합: ~37초
- DB 저장: ~1초
- **총 소요 시간: ~41초**

---

## 📊 성능 메트릭

| 항목 | 값 |
|------|-----|
| 바이너리 축소율 | 99.85% (1.7MB → 2.5KB) |
| 평균 분석 시간 | 41초 |
| AI 모델 호출 | 2회 (에이전트 + Orchestrator) |
| DB API 호출 | 4회 (GET 3회, POST 1회) |
| 지원 파일 타입 | 바이너리, 소스코드, 로그 |
| 병렬 처리 | DB GET 요청 3개 동시 실행 |

---

## 📚 관련 문서

- **`REPORT_FORMAT_SAMPLE.md`**: 보고서 형식 샘플 + 프론트엔드 파싱 가이드
- **`WORKFLOW_TEST_LOG.md`**: 전체 워크플로우 테스트 로그 (API 요청/응답)
- **`BINARY_PREPROCESSING_REPORT.md`**: Capstone 바이너리 전처리 상세 문서
- **`db_api_docs.txt`**: 백엔드 DB API 전체 문서

---

## 🔗 외부 DB API 연동

### DB API 엔드포인트

**Base URL**: `https://your-backend-api.ngrok-free.dev`

**데이터 조회** (GET):
- `GET /files/{file_id}/llm/?scan_id={scan_id}` - 어셈블리
- `GET /files/{file_id}/llm_code/?scan_id={scan_id}` - 코드
- `GET /files/{file_id}/llm_log/?scan_id={scan_id}` - 로그

**분석 결과 저장** (POST):
- `POST /files/{file_id}/llm_analysis/` - 종합 보고서 (마크다운)

### Request Body (분석 결과 저장)

```json
{
  "File_id": 1,
  "Scan_id": 1,
  "LLM_analysis": "# 1. 스캔 대상\n\n**File ID:** 1..."
}
```

---

## 🛠️ 개발 가이드

### 프로젝트 구조

```
AI-Server/
├── main.py                          # 서버 진입점
├── requirements.txt                 # Python 의존성
├── .env                            # 환경 변수 (API 키)
│
├── pqc_inspector_server/
│   ├── api/
│   │   ├── endpoints.py            # API 라우트 정의
│   │   └── schemas.py              # Pydantic 스키마
│   │
│   ├── agents/                     # AI 에이전트
│   │   ├── source_code.py          # 소스코드 분석 에이전트
│   │   ├── assembly_binary.py      # 어셈블리 분석 에이전트
│   │   └── logs_config.py          # 로그 분석 에이전트
│   │
│   ├── orchestrator/
│   │   └── controller.py           # 오케스트레이터 컨트롤러
│   │
│   ├── services/
│   │   ├── ai_service.py           # AI 모델 호출 서비스
│   │   ├── binary_preprocessor.py  # Capstone 전처리
│   │   └── embedding_service.py    # 임베딩 생성
│   │
│   ├── db/
│   │   └── api_client.py           # 외부 DB API 클라이언트
│   │
│   └── core/
│       └── config.py               # 설정 관리
│
└── data/
    ├── rag_knowledge_base/         # RAG 지식 베이스
    └── vector_db/                  # ChromaDB 벡터 DB
```

### 새로운 에이전트 추가

1. `pqc_inspector_server/agents/` 에 새 파일 생성
2. `BaseAgent` 클래스 상속
3. `analyze()` 메서드 구현
4. `controller.py`에 에이전트 등록

---

## 🔐 보안 고려사항

- ✅ API 키는 `.env` 파일로 관리 (`.gitignore` 필수)
- ✅ DB API 타임아웃 설정 (30초)
- ✅ 파일 크기 제한 (업로드 시)
- ✅ 입력 검증 (Pydantic 스키마)
- ⚠️ 프로덕션 환경에서는 인증/인가 추가 권장

---

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

---

## 🤝 기여

이슈 및 풀 리퀘스트는 GitHub에서 환영합니다!

---

**Made with ❤️ by PQC Inspector Team**
