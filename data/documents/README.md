# 📚 Documents Directory

이 디렉토리는 RAG 시스템에 추가할 공식 문서들을 저장하는 곳입니다.
**에이전트별로 분리된 디렉토리 구조**를 사용하여 각 전문 에이전트가 특화된 지식을 제공할 수 있습니다.

## 📄 지원하는 문서 형식

- **PDF**: `.pdf` - 공식 문서, 논문, 표준 문서
- **Microsoft Word**: `.docx` - 정책 문서, 가이드라인
- **마크다운**: `.md`, `.markdown` - 기술 문서, README
- **텍스트**: `.txt` - 일반 텍스트 문서
- **소스코드**: `.py`, `.c`, `.cpp`, `.h`, `.js`, `.java` - 예제 코드

## 🗂️ 에이전트별 디렉토리 구조

```
data/documents/
├── source_code/        # 소스코드 에이전트용 문서
│   ├── standards/
│   ├── libraries/
│   ├── examples/
│   └── api-docs/
├── binary/            # 바이너리 에이전트용 문서
│   ├── analysis-tools/
│   ├── reverse-eng/
│   └── assembly/
├── parameter/         # 파라미터 에이전트용 문서
│   ├── configs/
│   ├── policies/
│   └── settings/
└── log_conf/         # 로그/설정 에이전트용 문서
    ├── logging/
    ├── monitoring/
    └── audit/
```

## 🚀 문서 추가 방법

### 1. 에이전트별 디렉토리 전체 수집 (권장)
```bash
# 모든 에이전트 디렉토리의 문서를 한 번에 수집
python scripts/ingest_documents.py agent-dirs

# 특정 디렉토리 루트 지정
python scripts/ingest_documents.py agent-dirs --documents-root data/documents

# 재귀 검색 없이 수집
python scripts/ingest_documents.py agent-dirs --no-recursive
```

### 2. 단일 문서 추가
```bash
# 에이전트별 디렉토리에 파일 배치 후 수집 (자동 분류)
python scripts/ingest_documents.py file data/documents/source_code/nist-pqc-standard.pdf

# 특정 에이전트 타입 명시
python scripts/ingest_documents.py file data/documents/binary/analysis-guide.pdf --agent-type binary
```

### 3. 특정 에이전트 디렉토리 수집
```bash
# 소스코드 에이전트 디렉토리만 수집
python scripts/ingest_documents.py directory data/documents/source_code/ --agent-type source_code

# 파라미터 에이전트 디렉토리 수집
python scripts/ingest_documents.py directory data/documents/parameter/ --agent-type parameter
```

### 4. 여러 문서 배치 추가
```bash
# 여러 파일을 한 번에 추가
python scripts/ingest_documents.py batch \
  data/documents/source_code/nist-pqc.pdf \
  data/documents/binary/ghidra-manual.pdf \
  data/documents/parameter/openssl-config.md
```

## 🎯 문서 분류 가이드

### Source Code Agent
- 암호화 라이브러리 사용 예제
- 프로그래밍 가이드
- API 문서
- 코드 샘플

### Binary Agent
- 바이너리 분석 도구 문서
- 어셈블리 코드 예제
- 리버스 엔지니어링 가이드
- 실행 파일 분석 보고서

### Parameter Agent
- 설정 파일 가이드
- 정책 문서
- 구성 관리 문서
- 보안 설정 가이드

### Log/Conf Agent
- 로그 분석 가이드
- 시스템 설정 문서
- 모니터링 가이드
- 감사 로그 예제

## 💡 팁

1. **파일명 명명 규칙**: 내용을 쉽게 알 수 있는 명확한 이름 사용
2. **메타데이터 추가**: 가능하면 소스, 버전, 날짜 정보 포함
3. **정기 업데이트**: 새로운 표준이나 문서가 나오면 정기적으로 추가
4. **검증**: 수집 후 `validate` 명령으로 정상 수집 확인

## 🔍 수집 검증

문서가 정상적으로 수집되었는지 확인:

```bash
# 수집된 문서 검증
python scripts/ingest_documents.py validate data/documents/nist-pqc.pdf

# RAG 시스템 상태 확인
python scripts/manage_rag_data.py status

# 검색 테스트
python scripts/manage_rag_data.py test source_code "NIST PQC standard"
```