# PQC Inspector AI Server

양자내성암호(PQC) 전환을 위한 AI 기반 암호화 분석 시스템입니다. 소스코드, 바이너리, 로그/설정 파일에서 비양자내성암호(Non-PQC) 사용 여부를 탐지하고 분석합니다.

## 주요 기능

### AI 오케스트레이터
- **지능형 파일 분류**: 업로드된 파일을 AI가 자동 분석하여 적절한 전문 에이전트에 할당
- **결과 검증 및 요약**: 에이전트 분석 결과를 검토하고 최종 품질 보장
- **상용 AI API 활용**: GPT-4.1을 사용한 고성능 AI 처리

### RAG 강화 전문 에이전트 시스템
- **SourceCodeAgent**: 프로그래밍 언어 소스코드 전문 분석 (Gemini 2.5 Flash)
- **AssemblyBinaryAgent**: 어셈블리 및 바이너리 파일 분석 (Gemini 2.5 Flash)
- **LogsConfigAgent**: 로그 파일 및 서버 설정 분석 (Gemini 2.5 Flash)

### RAG (Retrieval-Augmented Generation) 시스템
- **벡터 데이터베이스**: ChromaDB를 활용한 고속 유사도 검색
- **전문 지식 베이스**: 에이전트별 특화된 암호화 패턴 및 취약점 정보
- **한국형 암호 알고리즘 지원**: SEED, ARIA, HIGHT, LEA, LSH, KCDSA 등
- **OpenAI 임베딩**: `text-embedding-3-small` 모델 사용

### 외부 API 통합
- **RESTful API 설계**: 다른 시스템과 쉽게 통합 가능
- **비동기 백그라운드 처리**: 대용량 파일 분석을 위한 효율적인 처리

## 시작하기

### 사전 준비
- **Python 3.9+**
- **OpenAI API 키**: GPT-4.1 및 임베딩 API 사용
- **Google API 키**: Gemini 2.5 Flash API 사용

### 설치 및 실행

#### 1. 프로젝트 클론
```bash
git clone https://github.com/BOB14th-project/AI-Server.git
cd AI-Server
```

#### 2. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (API 키 입력)
vim .env
```

`.env` 파일 예제:
```bash
# AI API 키
OPENAI_API_KEY="sk-proj-your-openai-key-here"
GOOGLE_API_KEY="your-google-api-key-here"

# 외부 API 설정
EXTERNAL_API_BASE_URL="https://api.example.com/v1"
EXTERNAL_API_KEY="your-api-key-here"

# 로그 레벨
LOG_LEVEL="INFO"
```

#### 3. Python 환경 설정
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. 서버 실행
```bash
python main.py
```

서버가 실행되면 RAG 시스템이 자동으로 초기화됩니다:
- ChromaDB 벡터 데이터베이스 로드
- 사전 구축된 암호화 패턴 지식 베이스 로드
- 각 에이전트별 전문 지식 임베딩 준비

#### 5. 접속 확인
- **로컬 접속**: http://127.0.0.1:8000
- **API 문서**: http://127.0.0.1:8000/docs

## 프로젝트 구조

```
AI-Server/
├── main.py                              # FastAPI 애플리케이션 진입점
├── requirements.txt                      # Python 의존성 패키지
├── .env                                 # 환경 변수 (API 키 등)
├── .env.example                         # 환경 변수 템플릿
├── .gitignore                           # Git 무시 파일 목록
│
├── pqc_inspector_server/                # 메인 서버 패키지
│   ├── api/                            # API 레이어
│   │   ├── endpoints.py                # FastAPI 라우터 및 엔드포인트
│   │   └── schemas.py                  # Pydantic 데이터 모델
│   │
│   ├── core/                           # 핵심 설정
│   │   └── config.py                   # 환경 설정 및 API 키 관리
│   │
│   ├── db/                             # 데이터베이스 레이어
│   │   └── api_client.py               # 외부 API 클라이언트
│   │
│   ├── agents/                         # AI 에이전트들
│   │   ├── base_agent.py               # RAG 강화 에이전트 기본 클래스
│   │   ├── source_code.py              # 소스코드 분석 에이전트
│   │   ├── assembly_binary.py          # 어셈블리/바이너리 분석 에이전트
│   │   └── logs_config.py              # 로그/설정 파일 분석 에이전트
│   │
│   ├── orchestrator/                   # 오케스트레이션
│   │   └── controller.py               # AI 오케스트레이터 (GPT-4.1)
│   │
│   └── services/                       # 서비스 레이어
│       ├── ai_service.py               # AI API 호출 서비스
│       ├── embedding_service.py        # 임베딩 생성 서비스
│       ├── vector_store.py             # ChromaDB 벡터 스토어 관리
│       ├── knowledge_manager.py        # 지식 베이스 관리
│       ├── document_ingestion.py       # 문서 수집 서비스
│       ├── document_processor.py       # 문서 처리 서비스
│       ├── model_loader.py             # AI 모델 로더
│       ├── ollama_service.py           # Ollama 로컬 모델 서비스
│       ├── preprocessing.py            # 데이터 전처리
│       ├── rag_manager.py              # RAG 시스템 관리
│       └── reporting.py                # 리포트 생성 서비스
│
├── data/                               # 데이터 디렉토리
│   ├── vector_db/                      # ChromaDB 벡터 데이터베이스 (사전 구축됨)
│   │   ├── chroma.sqlite3              # ChromaDB 메타데이터
│   │   ├── 02be4eba-.../               # source_code 에이전트 벡터 (73 docs)
│   │   ├── 0f768625-.../               # assembly_binary 에이전트 벡터 (76 docs)
│   │   ├── 76b8f68c-.../               # logs_config 에이전트 벡터 (161 docs)
│   │   └── [기타 컬렉션들]/
│   │
│   ├── rag_knowledge_base/             # RAG 지식 베이스 (JSON)
│   │   ├── source_code/                # 소스코드 분석 전문 지식
│   │   ├── assembly_binary/            # 바이너리 분석 전문 지식
│   │   │   └── reference_pdfs/         # 참고 PDF 문서
│   │   ├── logs_config/                # 로그/설정 분석 전문 지식
│   │   └── common/                     # 공통 지식
│   │       ├── korean_crypto_rag_reference.json  # 한국형 암호 알고리즘
│   │       └── reference_pdfs/         # 공통 참고 문서
│   │
│   ├── rag_knowledge_base_backup/      # 지식 베이스 백업
│   │   └── 20251030_000648/            # 타임스탬프별 백업
│   │
│   ├── documents/                      # 원본 문서 저장소
│   │   ├── source_code/                # 소스코드 관련 문서
│   │   ├── binary/                     # 바이너리 관련 문서
│   │   ├── log_conf/                   # 로그/설정 관련 문서
│   │   └── parameter/                  # 파라미터 관련 문서
│   │
│   └── fine_tuning_data/               # 파인튜닝 데이터
│
├── scripts/                            # 유틸리티 스크립트
│   ├── manage_rag_data.py              # RAG 데이터 관리 도구
│   ├── ingest_documents.py             # 문서 수집 스크립트
│   ├── rebuild_all_vector_dbs.py       # 전체 벡터 DB 재구축
│   ├── rebuild_binary_vector_db.py     # 바이너리 벡터 DB 재구축
│   ├── optimize_binary_rag.py          # 바이너리 RAG 최적화
│   ├── setup_db.py                     # 데이터베이스 셋업
│   ├── run_finetune.py                 # 파인튜닝 실행
│   ├── test_rag_improvements.py        # RAG 개선 테스트
│   └── test_final_improvements.py      # 최종 개선 테스트
│
├── test/                               # 테스트 파일
│   ├── test_rsa.py                     # RSA 테스트 (쉬움)
│   ├── test_hidden_crypto.py           # 숨겨진 암호화 테스트 (중간)
│   ├── test_stealth_crypto.c           # 위장된 C 암호화 (어려움)
│   └── [기타 테스트 파일들]
│
├── test_crypto.py                      # 암호화 테스트
├── test_rag_quality.py                 # RAG 품질 테스트
├── test.log                            # 테스트 로그 샘플
├── benchmark.md                        # 벤치마크 결과
└── db_api_docs.txt                     # DB API 문서
```

## 디렉토리 설명

### `/pqc_inspector_server` - 메인 서버 애플리케이션
서버의 핵심 로직이 포함된 패키지입니다.

- **`api/`**: FastAPI 엔드포인트 및 데이터 스키마
- **`core/`**: 환경 설정 및 전역 설정 관리
- **`db/`**: 외부 API와의 통신 클라이언트
- **`agents/`**: 파일 타입별 전문 분석 에이전트
- **`orchestrator/`**: 에이전트 조율 및 워크플로우 관리
- **`services/`**: AI, 임베딩, 벡터 스토어, 문서 처리 등 서비스

### `/data` - 데이터 저장소
모든 데이터 관련 파일이 저장됩니다.

- **`vector_db/`**: ChromaDB 벡터 데이터베이스 (사전 구축됨, 약 16MB)
  - 73개 문서 (source_code)
  - 76개 문서 (assembly_binary)
  - 161개 문서 (logs_config)
  - 한국형 암호 알고리즘 포함 (SEED, ARIA, HIGHT, LEA, LSH, KCDSA)

- **`rag_knowledge_base/`**: JSON 형식의 RAG 지식 베이스
  - 에이전트별 특화된 암호화 패턴 및 탐지 규칙
  - PDF 참고 문서 포함

- **`documents/`**: 원본 문서 저장소
- **`fine_tuning_data/`**: AI 모델 파인튜닝용 데이터

### `/scripts` - 유틸리티 스크립트
데이터베이스 관리 및 유지보수를 위한 도구들입니다.

- **`manage_rag_data.py`**: RAG 지식 베이스 관리 (추가/삭제/조회/통계)
- **`ingest_documents.py`**: 새 문서를 RAG 시스템에 추가
- **`rebuild_all_vector_dbs.py`**: 전체 벡터 데이터베이스 재구축

### `/test` - 테스트 파일
AI 탐지 능력을 검증하기 위한 다양한 난이도의 테스트 케이스입니다.

## API 엔드포인트

### 기본 엔드포인트
- **GET `/`**: 서버 상태 확인
- **GET `/docs`**: Swagger UI API 문서
- **GET `/redoc`**: ReDoc API 문서

### 분석 엔드포인트
- **POST `/api/v1/analyze`**: 파일 분석 요청
  ```bash
  curl -X POST "http://localhost:8000/api/v1/analyze" \
       -H "accept: application/json" \
       -H "Content-Type: multipart/form-data" \
       -F "file=@test/test_rsa.py"
  ```

- **GET `/api/v1/report/{report_id}`**: 분석 결과 조회
  ```bash
  curl -X GET "http://localhost:8000/api/v1/report/{report_id}"
  ```

### 응답 형식
```json
{
  "report_id": "unique-report-identifier",
  "file_name": "test_rsa.py",
  "file_type": "source_code",
  "is_pqc_vulnerable": true,
  "vulnerability_details": "RSA 2048-bit encryption detected",
  "detected_algorithms": ["RSA"],
  "recommendations": "Replace with CRYSTALS-Kyber",
  "evidence": "import rsa, rsa.newkeys(2048)",
  "confidence_score": 0.95
}
```

## RAG 시스템 사용법

### RAG 데이터 관리

#### 지식 추가
```bash
# 소스코드 에이전트에 새 패턴 추가
python scripts/manage_rag_data.py add source_code "RSA-4096 사용 패턴: ..."

# 바이너리 에이전트에 새 패턴 추가
python scripts/manage_rag_data.py add assembly_binary "OpenSSL 시그니처: ..."
```

#### 통계 확인
```bash
# 전체 RAG 데이터 통계
python scripts/manage_rag_data.py stats
```

#### 백업 및 복원
```bash
# 백업 (자동으로 타임스탬프 디렉토리 생성)
python scripts/manage_rag_data.py backup

# 특정 백업으로 복원
python scripts/manage_rag_data.py restore data/rag_knowledge_base_backup/20251030_000648
```

### 문서 추가

```bash
# PDF 문서 추가
python scripts/ingest_documents.py file data/documents/nist-pqc-standard.pdf

# 디렉토리 전체 문서 추가
python scripts/ingest_documents.py directory data/documents/
```

### 벡터 DB 재구축

```bash
# 전체 벡터 데이터베이스 재구축
python scripts/rebuild_all_vector_dbs.py

# 특정 에이전트만 재구축
python scripts/rebuild_binary_vector_db.py
```

## AI 모델 정보

| 역할 | 모델 | 용도 |
|------|------|------|
| 오케스트레이터 | GPT-4.1 | 파일 분류, 결과 검증 |
| 소스코드 분석 | Gemini 2.5 Flash | 프로그래밍 언어 코드 분석 |
| 바이너리 분석 | Gemini 2.5 Flash | 어셈블리/바이너리 파일 분석 |
| 로그/설정 분석 | Gemini 2.5 Flash | 로그 및 설정파일 분석 |
| 임베딩 생성 | OpenAI text-embedding-3-small | 벡터 임베딩 |

## 사전 구축된 벡터 데이터베이스

이 프로젝트는 **사전 구축된 벡터 데이터베이스**를 포함하고 있어 즉시 사용 가능합니다:

- **총 크기**: 약 16MB
- **총 문서 수**: 310개
  - source_code: 73 documents
  - assembly_binary: 76 documents
  - logs_config: 161 documents
- **한국형 암호 알고리즘**: SEED, ARIA, HIGHT, LEA, LSH, KCDSA
- **장점**:
  - 새 환경에서 벡터 DB 재구축 불필요
  - 즉시 배포 가능
  - 일관된 RAG 성능 보장

## 테스트 방법

```bash
# 서버 실행
python main.py

# 다른 터미널에서 테스트
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -F "file=@test/test_rsa.py"
```

## 라이선스

MIT License
