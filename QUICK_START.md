# ⚡ PQC Inspector AI Server - 빠른 시작 가이드

**5분 안에 서버를 실행하고 외부 접근을 설정하세요!**

---

## 📋 준비물

- Python 3.9 이상
- OpenAI API 키
- Google API 키
- 인터넷 연결

---

## 🚀 빠른 설치 (5분)

### 1. 프로젝트 클론 및 설치

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-org/AI-Server.git
cd AI-Server

# 2. 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 패키지 설치 (5-10분 소요)
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
nano .env
```

**`.env` 파일 내용**:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
GOOGLE_API_KEY=your-google-key-here
EXTERNAL_API_BASE_URL=https://your-backend-api.com

ORCHESTRATOR_MODEL=gpt-4o-mini
SOURCE_CODE_MODEL=gemini-2.0-flash-exp
BINARY_MODEL=gemini-2.0-flash-exp
LOG_CONF_MODEL=gemini-2.0-flash-exp

SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

### 3. 서버 실행

```bash
python main.py
```

### 4. 테스트

```bash
# 다른 터미널에서
curl http://127.0.0.1:8000/
# 출력: {"message":"PQC Inspector 서버가 정상적으로 실행 중입니다!"}
```

---

## 🌐 외부 접근 설정 (ngrok)

### 1. ngrok 설치

**macOS**:
```bash
brew install ngrok/ngrok/ngrok
```

**Linux**:
```bash
sudo snap install ngrok
```

**Windows**:
```powershell
choco install ngrok
```

### 2. ngrok 인증

```bash
# 1. https://dashboard.ngrok.com/signup 에서 회원가입
# 2. https://dashboard.ngrok.com/get-started/your-authtoken 에서 토큰 복사
# 3. 인증
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 3. 터널 시작

**터미널 1 - AI 서버**:
```bash
source .venv/bin/activate
python main.py
```

**터미널 2 - ngrok**:
```bash
ngrok http 8000
```

### 4. URL 확인 및 공유

ngrok 출력에서 `Forwarding` URL을 확인:
```
Forwarding    https://1a2b-3c4d-5e6f.ngrok-free.app -> http://localhost:8000
```

**이 URL을 프론트엔드 개발자에게 공유하세요!**

### 5. 외부에서 테스트

```bash
curl https://1a2b-3c4d-5e6f.ngrok-free.app/
```

---

## 📝 API 엔드포인트

### 개별 파일 분석
```bash
curl -X POST "https://your-ngrok-url.ngrok-free.app/api/v1/analyze/db?file_id=1&scan_id=1"
```

### 전체 파일 일괄 분석
```bash
curl -X POST "https://your-ngrok-url.ngrok-free.app/api/v1/analyze/db/all?scan_id=1&max_files=10"
```

### API 문서 (Swagger UI)
```
https://your-ngrok-url.ngrok-free.app/docs
```

---

## 🔧 문제 해결

### 포트 이미 사용 중
```bash
lsof -i :8000
kill -9 <PID>
```

### API 키 오류
```bash
cat .env | grep API_KEY
# 키가 올바르게 설정되어 있는지 확인
```

### 패키지 import 오류
```bash
# 가상환경 확인
which python
# 출력: .../AI-Server/.venv/bin/python

# 패키지 재설치
pip install -r requirements.txt
```

---

## 📚 추가 문서

- **SERVER_DEPLOYMENT_GUIDE.md**: 전체 배포 가이드 (프로덕션 환경)
- **FRONTEND_API_RESPONSE_FORMAT.md**: API 응답 포맷 및 통합 예제
- **README.md**: 프로젝트 개요 및 아키텍처

---

## ✅ 완료!

이제 다음을 사용할 수 있습니다:
- ✅ 로컬 서버: `http://127.0.0.1:8000`
- ✅ 외부 접근: `https://your-ngrok-url.ngrok-free.app`
- ✅ API 문서: `https://your-ngrok-url.ngrok-free.app/docs`

**질문이 있으신가요? GitHub Issues를 통해 문의해주세요!**
