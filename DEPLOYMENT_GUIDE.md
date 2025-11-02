# 배포 가이드

새로운 환경에서 AI 서버를 설정하는 방법입니다.

## 벡터 DB 관리 전략

현재 벡터 DB는 `.gitignore`에 포함되어 Git에 커밋되지 않습니다.

### 현재 상태
- 벡터 DB 크기: **16MB**
- 위치: `data/vector_db/`
- 상태: Git에서 **제외됨** (`.gitignore`의 69번째 줄)

### 옵션 1: 벡터 DB를 Git에 포함 (권장)

**설정 방법:**
```bash
# .gitignore에서 벡터 DB 제외 규칙 제거
# 69-70번째 줄 주석 처리 또는 삭제:
# data/vector_db/
# chroma_db/

# 벡터 DB 커밋
git add data/vector_db/
git commit -m "Add pre-built vector database for quick deployment"
git push
```

**다른 컴퓨터에서 사용:**
```bash
# 1. 저장소 클론
git clone <repository-url>
cd AI-Server

# 2. 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. .env 파일 생성 (API 키 설정)
cp .env.example .env
# .env 파일 편집하여 API 키 입력

# 4. 서버 실행 (벡터 DB는 이미 포함됨)
uvicorn main:app --host 0.0.0.0 --port 8000
```

**장점:**
- 즉시 사용 가능
- API 키 없이도 RAG 기능 동작
- 일관된 임베딩 보장

**단점:**
- Git 저장소 크기 +16MB

---

### 옵션 2: 벡터 DB를 Git에서 제외 (현재 방식)

**다른 컴퓨터에서 사용:**
```bash
# 1. 저장소 클론
git clone <repository-url>
cd AI-Server

# 2. 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. .env 파일 생성 (⚠️ GOOGLE_API_KEY 필수!)
cp .env.example .env
# .env 파일 편집:
# GOOGLE_API_KEY=your-actual-api-key-here

# 4. 벡터 DB 재구축 (약 1-2분 소요)
python scripts/manage_rag_data.py refresh

# 5. 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

**장점:**
- Git 저장소 가볍게 유지
- JSON만 버전 관리

**단점:**
- Google API 키 필수
- 재구축 시간 필요 (1-2분)
- 임베딩 모델 버전 차이 가능

---

## 권장 사항

### 개발/프로덕션 환경 → 옵션 1 사용
- 빠른 배포
- 일관성 보장
- 16MB는 충분히 작은 크기

### CI/CD 파이프라인 → 옵션 2 사용
- 깨끗한 빌드
- 항상 최신 임베딩

---

## 벡터 DB 관리 명령어

### 상태 확인
```bash
python scripts/manage_rag_data.py status
```

### 전체 재구축
```bash
python scripts/manage_rag_data.py refresh
```

### 특정 에이전트만 재구축
```bash
python scripts/manage_rag_data.py refresh source_code
python scripts/manage_rag_data.py refresh assembly_binary
python scripts/manage_rag_data.py refresh logs_config
```

### 검색 테스트
```bash
python scripts/manage_rag_data.py test source_code "RSA encryption"
```

---

## 환경 변수 (.env)

필수 환경 변수:
```
# AI API Keys
OPENAI_API_KEY=your-openai-key-here
GOOGLE_API_KEY=your-google-api-key-here  # 벡터 DB 재구축 시 필수

# DB API (이미 설정됨)
EXTERNAL_API_BASE_URL=https://harper-abler-agape.ngrok-free.dev
```

---

## 배포 체크리스트

### 초기 설정
- [ ] Git 클론
- [ ] Python 가상환경 생성
- [ ] 의존성 설치 (`pip install -r requirements.txt`)
- [ ] `.env` 파일 생성 및 API 키 설정
- [ ] (옵션 2의 경우) 벡터 DB 재구축

### 서버 실행 전
- [ ] 벡터 DB 상태 확인 (`python scripts/manage_rag_data.py status`)
- [ ] 포트 8000 사용 가능 확인
- [ ] 네트워크 연결 확인 (DB API 접근)

### 서버 실행
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 헬스 체크
```bash
curl http://localhost:8000/
curl http://localhost:8000/api/v1/
```

---

## 문제 해결

### 벡터 DB가 비어있음
```bash
python scripts/manage_rag_data.py refresh
```

### 임베딩 생성 실패
- `.env`에 `GOOGLE_API_KEY` 설정 확인
- API 키 유효성 확인
- 네트워크 연결 확인

### 서버 실행 오류
```bash
# 로그 확인
tail -f *.log

# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```
