# 🚀 PQC Inspector AI Server 배포 가이드

**최종 업데이트**: 2025-11-20
**서버 버전**: v1.0
**Python 요구사항**: Python 3.9 이상 (Python 3.13 권장)

---

## 📋 목차

1. [서버 설치 가이드](#1-서버-설치-가이드)
2. [ngrok을 이용한 외부 접근 설정](#2-ngrok을-이용한-외부-접근-설정)
3. [환경 변수 설정](#3-환경-변수-설정)
4. [서버 실행 및 관리](#4-서버-실행-및-관리)
5. [프로덕션 배포](#5-프로덕션-배포)
6. [문제 해결](#6-문제-해결)

---

## 1. 서버 설치 가이드

### 1.1 시스템 요구사항

#### 최소 요구사항
- **OS**: Linux, macOS, Windows 10/11
- **CPU**: 2코어 이상
- **RAM**: 4GB 이상
- **저장공간**: 5GB 이상 (모델 캐시 포함)
- **Python**: 3.9 이상 (3.13 권장)
- **네트워크**: 인터넷 연결 필수 (AI API 호출용)

#### 권장 요구사항
- **CPU**: 4코어 이상
- **RAM**: 8GB 이상
- **저장공간**: 10GB 이상
- **Python**: 3.13

---

### 1.2 새 서버에 프로젝트 설치하기

#### Step 1: Git 저장소 클론

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-org/AI-Server.git
cd AI-Server

# 2. 브랜치 확인 (main 또는 production 브랜치 사용)
git checkout main
```

#### Step 2: Python 가상환경 생성

```bash
# Python 3.9+ 설치 확인
python3 --version
# 출력 예: Python 3.13.0

# 가상환경 생성
python3 -m venv .venv

# 가상환경 활성화
# Linux/macOS:
source .venv/bin/activate

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (cmd):
.venv\Scripts\activate.bat
```

#### Step 3: 패키지 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 프로젝트 의존성 설치
pip install -r requirements.txt

# 설치 확인 (주요 패키지)
python -c "import fastapi; import chromadb; import capstone; print('✅ 모든 패키지가 정상적으로 설치되었습니다!')"
```

**예상 설치 시간**: 5-10분 (인터넷 속도에 따라 다름)

**용량**: 약 3-4GB (torch, transformers 등 포함)

#### Step 4: 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 에디터로 .env 파일 편집
nano .env
# 또는
vim .env
```

`.env` 파일 내용 (아래 섹션 3 참고):

```bash
# AI API 키
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# 외부 DB API 설정
EXTERNAL_API_BASE_URL=https://your-backend-api.com

# AI 모델 설정
ORCHESTRATOR_MODEL=gpt-4o-mini
SOURCE_CODE_MODEL=gemini-2.0-flash-exp
BINARY_MODEL=gemini-2.0-flash-exp
LOG_CONF_MODEL=gemini-2.0-flash-exp

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

#### Step 5: 서버 실행 테스트

```bash
# 서버 실행 (개발 모드)
python main.py

# 다른 터미널에서 테스트
curl http://127.0.0.1:8000/
# 출력: {"message":"PQC Inspector 서버가 정상적으로 실행 중입니다!"}
```

**축하합니다! 서버 설치가 완료되었습니다! 🎉**

---

## 2. ngrok을 이용한 외부 접근 설정

### 2.1 ngrok이란?

ngrok은 로컬 서버를 인터넷에 공개할 수 있는 터널링 서비스입니다.

**장점**:
- 🌐 외부 네트워크에서 로컬 서버 접근 가능
- 🔒 HTTPS 자동 제공
- 🚀 방화벽/NAT 우회
- 📊 실시간 트래픽 모니터링

**사용 사례**:
- 다른 컴퓨터/네트워크에서 AI 서버 접근
- 프론트엔드 개발자와 협업
- 데모 및 테스트

---

### 2.2 ngrok 설치 및 설정

#### Step 1: ngrok 설치

**macOS (Homebrew)**:
```bash
brew install ngrok/ngrok/ngrok
```

**Linux**:
```bash
# Snap 사용
sudo snap install ngrok

# 또는 직접 다운로드
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

**Windows**:
```powershell
# Chocolatey 사용
choco install ngrok

# 또는 공식 사이트에서 다운로드
# https://ngrok.com/download
```

#### Step 2: ngrok 계정 생성 및 인증

```bash
# 1. ngrok 회원가입 (무료)
# https://dashboard.ngrok.com/signup

# 2. Authtoken 복사
# https://dashboard.ngrok.com/get-started/your-authtoken

# 3. Authtoken 설정
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE

# 예시:
# ngrok config add-authtoken 2abc123def456ghi789jkl012mno345
```

#### Step 3: AI 서버와 ngrok 동시 실행

**터미널 1 - AI 서버 실행**:
```bash
# 가상환경 활성화
source .venv/bin/activate

# 서버 실행
python main.py
```

**터미널 2 - ngrok 터널 시작**:
```bash
# HTTP 터널 시작 (포트 8000)
ngrok http 8000
```

#### Step 4: ngrok URL 확인

ngrok 실행 후 다음과 같은 출력이 나타납니다:

```
ngrok

Session Status                online
Account                       your_email@example.com (Plan: Free)
Version                       3.x.x
Region                        Asia Pacific (ap)
Latency                       25ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://1a2b-3c4d-5e6f.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**중요한 정보**:
- **Forwarding URL**: `https://1a2b-3c4d-5e6f.ngrok-free.app`
  - 이 URL을 프론트엔드 개발자에게 공유하세요!
- **Web Interface**: `http://127.0.0.1:4040`
  - 브라우저에서 실시간 요청/응답 모니터링 가능

#### Step 5: 외부에서 API 테스트

```bash
# 다른 컴퓨터 또는 네트워크에서 테스트
curl https://1a2b-3c4d-5e6f.ngrok-free.app/
# 출력: {"message":"PQC Inspector 서버가 정상적으로 실행 중입니다!"}

# 개별 파일 분석 테스트
curl -X POST "https://1a2b-3c4d-5e6f.ngrok-free.app/api/v1/analyze/db?file_id=1&scan_id=1"
```

---

### 2.3 프론트엔드에 ngrok URL 전달

#### 방법 1: .env 파일 업데이트

**프론트엔드 프로젝트의 `.env` 파일**:
```bash
# .env (React, Next.js 등)
VITE_API_BASE_URL=https://1a2b-3c4d-5e6f.ngrok-free.app
# 또는
REACT_APP_API_BASE_URL=https://1a2b-3c4d-5e6f.ngrok-free.app
# 또는
NEXT_PUBLIC_API_BASE_URL=https://1a2b-3c4d-5e6f.ngrok-free.app
```

#### 방법 2: API 클라이언트에서 직접 설정

```typescript
// apiClient.ts
const API_BASE_URL = "https://1a2b-3c4d-5e6f.ngrok-free.app";

export async function analyzeFile(fileId: number, scanId: number) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/analyze/db?file_id=${fileId}&scan_id=${scanId}`,
    { method: "POST" }
  );
  return response.json();
}
```

---

### 2.4 ngrok 유료 플랜 비교

| 기능 | Free | Basic ($10/월) | Pro ($20/월) |
|------|------|----------------|---------------|
| 동시 터널 수 | 1개 | 3개 | 10개 |
| 도메인 | 랜덤 | 커스텀 | 커스텀 |
| 세션 시간 | 8시간 | 무제한 | 무제한 |
| 대역폭 | 제한적 | 더 많음 | 무제한 |

**추천**: 개발/테스트 용도는 Free 플랜으로 충분합니다!

---

### 2.5 ngrok 대안 (선택사항)

ngrok 외에도 다음 서비스를 사용할 수 있습니다:

1. **localhost.run** (무료, 가장 간단)
   ```bash
   ssh -R 80:localhost:8000 nokey@localhost.run
   ```

2. **Cloudflare Tunnel** (무료, 더 안정적)
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```

3. **Serveo** (무료)
   ```bash
   ssh -R 80:localhost:8000 serveo.net
   ```

---

## 3. 환경 변수 설정

### 3.1 필수 환경 변수

#### OpenAI API 키 발급

1. [OpenAI Platform](https://platform.openai.com/)에 로그인
2. `API Keys` 메뉴 이동
3. `Create new secret key` 클릭
4. 키 복사 (예: `sk-proj-abc123...`)

**사용 모델**:
- `gpt-4o-mini`: AI Orchestrator (종합 보고서 생성)
- `text-embedding-3-small`: RAG 임베딩

#### Google API 키 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
2. `Get API key` 클릭
3. 키 생성 및 복사

**사용 모델**:
- `gemini-2.0-flash-exp`: 모든 에이전트 (소스코드, 어셈블리, 로그 분석)

#### 외부 DB API URL 설정

```bash
# 백엔드 서버 URL (예시)
EXTERNAL_API_BASE_URL=https://backend.example.com

# ngrok으로 백엔드 서버를 공개한 경우
EXTERNAL_API_BASE_URL=https://abc123.ngrok-free.app
```

---

### 3.2 .env 파일 전체 예시

```bash
# =====================================================
# PQC Inspector AI Server - 환경 변수
# =====================================================

# ===== AI API 키 =====
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz
GOOGLE_API_KEY=AIzaSyAbc123Def456Ghi789Jkl012Mno345Pqr678

# ===== 외부 DB API 설정 =====
EXTERNAL_API_BASE_URL=https://backend-api.ngrok-free.app

# ===== AI 모델 설정 =====
# AI Orchestrator 모델 (종합 리포트 생성)
ORCHESTRATOR_MODEL=gpt-4o-mini

# 에이전트 모델 (소스코드, 어셈블리, 로그 분석)
SOURCE_CODE_MODEL=gemini-2.0-flash-exp
BINARY_MODEL=gemini-2.0-flash-exp
LOG_CONF_MODEL=gemini-2.0-flash-exp

# ===== 서버 설정 =====
# 서버 호스트 (0.0.0.0 = 모든 네트워크 인터페이스에서 접근 허용)
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# ===== RAG 설정 (선택적) =====
# 벡터 DB 경로 (기본값: ./data/vector_db)
VECTOR_DB_PATH=./data/vector_db

# 임베딩 모델 (기본값: text-embedding-3-small)
EMBEDDING_MODEL=text-embedding-3-small

# ===== 기타 설정 (선택적) =====
# API 타임아웃 (초)
API_TIMEOUT=120

# 최대 파일 크기 (MB)
MAX_FILE_SIZE=50
```

---

### 3.3 환경 변수 보안

#### 중요: `.env` 파일은 절대 커밋하지 마세요!

```bash
# .gitignore 파일에 추가
echo ".env" >> .gitignore
```

#### 서버 환경에서 환경 변수 설정 (권장)

**Linux/macOS (systemd 서비스)**:
```ini
# /etc/systemd/system/pqc-inspector.service
[Service]
Environment="OPENAI_API_KEY=sk-proj-..."
Environment="GOOGLE_API_KEY=AIza..."
Environment="EXTERNAL_API_BASE_URL=https://backend.com"
```

**Docker 사용 시**:
```bash
docker run -d \
  -e OPENAI_API_KEY=sk-proj-... \
  -e GOOGLE_API_KEY=AIza... \
  -e EXTERNAL_API_BASE_URL=https://backend.com \
  -p 8000:8000 \
  pqc-inspector:latest
```

---

## 4. 서버 실행 및 관리

### 4.1 개발 모드 실행

```bash
# 가상환경 활성화
source .venv/bin/activate

# 서버 실행 (자동 재시작 활성화)
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### 4.2 프로덕션 모드 실행

#### 방법 1: nohup 사용 (간단)

```bash
# 백그라운드 실행
nohup python main.py > server.log 2>&1 &

# PID 확인
ps aux | grep "python main.py"

# 서버 종료
kill <PID>
```

#### 방법 2: systemd 서비스 (권장)

**Step 1: 서비스 파일 생성**

```bash
sudo nano /etc/systemd/system/pqc-inspector.service
```

**서비스 파일 내용**:
```ini
[Unit]
Description=PQC Inspector AI Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/AI-Server
Environment="PATH=/home/your_username/AI-Server/.venv/bin"
ExecStart=/home/your_username/AI-Server/.venv/bin/python /home/your_username/AI-Server/main.py
Restart=always
RestartSec=10

# 환경 변수 (선택적 - .env 파일 사용 권장)
# Environment="OPENAI_API_KEY=sk-proj-..."
# Environment="GOOGLE_API_KEY=AIza..."

[Install]
WantedBy=multi-user.target
```

**Step 2: 서비스 등록 및 실행**

```bash
# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable pqc-inspector

# 서비스 시작
sudo systemctl start pqc-inspector

# 상태 확인
sudo systemctl status pqc-inspector

# 로그 확인
sudo journalctl -u pqc-inspector -f
```

**Step 3: 서비스 관리 명령어**

```bash
# 서비스 중지
sudo systemctl stop pqc-inspector

# 서비스 재시작
sudo systemctl restart pqc-inspector

# 서비스 비활성화
sudo systemctl disable pqc-inspector
```

#### 방법 3: Docker 사용

**Dockerfile**:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["python", "main.py"]
```

**Docker 빌드 및 실행**:
```bash
# 이미지 빌드
docker build -t pqc-inspector:latest .

# 컨테이너 실행
docker run -d \
  --name pqc-inspector \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=sk-proj-... \
  -e GOOGLE_API_KEY=AIza... \
  -e EXTERNAL_API_BASE_URL=https://backend.com \
  pqc-inspector:latest

# 로그 확인
docker logs -f pqc-inspector

# 컨테이너 중지
docker stop pqc-inspector

# 컨테이너 삭제
docker rm pqc-inspector
```

---

### 4.3 서버 모니터링

#### 로그 확인

```bash
# systemd 서비스 로그
sudo journalctl -u pqc-inspector -f

# 파일 로그 (nohup 사용 시)
tail -f server.log

# Docker 로그
docker logs -f pqc-inspector
```

#### 서버 상태 확인

```bash
# 헬스 체크
curl http://127.0.0.1:8000/

# API 문서 접근
curl http://127.0.0.1:8000/docs
```

#### 리소스 모니터링

```bash
# CPU/메모리 사용량
top
# 또는
htop

# 특정 프로세스 모니터링
ps aux | grep python

# 포트 사용 확인
lsof -i :8000
# 또는
netstat -tulpn | grep 8000
```

---

## 5. 프로덕션 배포

### 5.1 클라우드 배포 옵션

#### AWS EC2

**권장 인스턴스**: `t3.medium` (2 vCPU, 4GB RAM)

```bash
# 1. EC2 인스턴스 생성 (Ubuntu 22.04 LTS)

# 2. SSH 접속
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# 3. 프로젝트 설치 (위 섹션 1 참고)

# 4. 방화벽 설정 (포트 8000 허용)
sudo ufw allow 8000

# 5. systemd 서비스로 실행 (위 섹션 4.2 참고)
```

#### Google Cloud Platform (GCP)

**권장 인스턴스**: `e2-medium` (2 vCPU, 4GB RAM)

```bash
# 1. Compute Engine VM 생성

# 2. SSH 접속
gcloud compute ssh your-instance-name

# 3. 프로젝트 설치 및 실행
```

#### DigitalOcean

**권장 Droplet**: `Basic - $24/월` (2 vCPU, 4GB RAM)

#### Heroku

```bash
# Procfile 생성
echo "web: python main.py" > Procfile

# Heroku 배포
heroku login
heroku create your-app-name
git push heroku main
```

---

### 5.2 리버스 프록시 설정 (Nginx)

**Nginx 설치**:
```bash
sudo apt update
sudo apt install nginx
```

**Nginx 설정 파일**:
```bash
sudo nano /etc/nginx/sites-available/pqc-inspector
```

**설정 내용**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 타임아웃 설정 (분석 시간 고려)
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

**Nginx 활성화**:
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/pqc-inspector /etc/nginx/sites-enabled/

# Nginx 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

**SSL 인증서 설정 (Let's Encrypt)**:
```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# SSL 인증서 발급 및 자동 설정
sudo certbot --nginx -d your-domain.com

# 자동 갱신 설정 (cron)
sudo certbot renew --dry-run
```

---

### 5.3 성능 최적화

#### Gunicorn 사용 (멀티 워커)

```bash
# Gunicorn 설치
pip install gunicorn

# 서버 실행 (워커 4개)
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

#### 권장 워커 수 공식
```
워커 수 = (2 × CPU 코어 수) + 1
```

---

## 6. 문제 해결

### 6.1 일반적인 문제

#### 문제 1: 포트 이미 사용 중

**에러 메시지**:
```
ERROR: [Errno 48] Address already in use
```

**해결 방법**:
```bash
# 포트 8000 사용 중인 프로세스 찾기
lsof -i :8000

# 프로세스 종료
kill -9 <PID>

# 또는 다른 포트 사용
SERVER_PORT=8001 python main.py
```

#### 문제 2: API 키 인증 실패

**에러 메시지**:
```
AuthenticationError: Invalid API key
```

**해결 방법**:
```bash
# .env 파일 확인
cat .env | grep API_KEY

# 환경 변수 로드 확인
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10])"

# API 키 유효성 테스트
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### 문제 3: 패키지 import 오류

**에러 메시지**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**해결 방법**:
```bash
# 가상환경 활성화 확인
which python
# 출력: /path/to/AI-Server/.venv/bin/python

# 패키지 재설치
pip install -r requirements.txt
```

#### 문제 4: ngrok 터널이 자주 끊김

**원인**: Free 플랜은 8시간 세션 제한

**해결 방법**:
```bash
# 자동 재시작 스크립트 (tunnel_restart.sh)
#!/bin/bash
while true; do
    ngrok http 8000
    sleep 5
done

# 실행
chmod +x tunnel_restart.sh
./tunnel_restart.sh
```

#### 문제 5: DB 연결 실패

**에러 메시지**:
```
HTTPError: 404 Not Found
```

**해결 방법**:
```bash
# 외부 DB API URL 확인
echo $EXTERNAL_API_BASE_URL

# DB API 접근 테스트
curl https://backend-api.com/files/1/llm/?scan_id=1

# .env 파일 업데이트 후 서버 재시작
```

---

### 6.2 성능 문제

#### 분석 속도가 너무 느림

**원인**:
- AI API 응답 지연
- 네트워크 지연
- 큰 파일 처리

**해결 방법**:
1. 더 빠른 인터넷 연결 사용
2. AI 모델 타임아웃 증가:
   ```bash
   API_TIMEOUT=300  # .env에 추가
   ```
3. 파일 크기 제한:
   ```bash
   MAX_FILE_SIZE=10  # 10MB로 제한
   ```

#### 메모리 부족

**에러 메시지**:
```
MemoryError: Unable to allocate array
```

**해결 방법**:
1. 더 많은 RAM 할당 (최소 8GB 권장)
2. Swap 메모리 추가 (Linux):
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

---

### 6.3 로그 분석

#### 에러 로그 확인

```bash
# systemd 서비스 로그 (최근 100줄)
sudo journalctl -u pqc-inspector -n 100

# 에러만 필터링
sudo journalctl -u pqc-inspector | grep ERROR

# 특정 시간대 로그
sudo journalctl -u pqc-inspector --since "2025-01-20 10:00:00"
```

#### 디버그 모드 활성화

```bash
# .env 파일 수정
LOG_LEVEL=DEBUG

# 서버 재시작
sudo systemctl restart pqc-inspector
```

---

## 7. 체크리스트

### 배포 전 체크리스트

- [ ] Python 3.9+ 설치 확인
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 패키지 설치
- [ ] .env 파일 설정 (API 키, DB URL)
- [ ] 서버 실행 테스트 (`curl http://127.0.0.1:8000/`)
- [ ] ngrok 설치 및 인증
- [ ] ngrok 터널 실행 및 URL 확인
- [ ] 외부에서 API 접근 테스트
- [ ] 프론트엔드에 ngrok URL 전달
- [ ] .env 파일이 .gitignore에 포함되어 있는지 확인

### 프로덕션 배포 체크리스트

- [ ] 클라우드 인스턴스 생성 (AWS, GCP, DigitalOcean 등)
- [ ] 방화벽 설정 (포트 8000 또는 80/443 허용)
- [ ] systemd 서비스 등록
- [ ] Nginx 리버스 프록시 설정
- [ ] SSL 인증서 설치 (Let's Encrypt)
- [ ] 로그 모니터링 설정
- [ ] 백업 계획 수립
- [ ] 문서화 완료

---

## 8. 추가 리소스

### 공식 문서
- **FastAPI**: https://fastapi.tiangolo.com/
- **ngrok**: https://ngrok.com/docs
- **OpenAI API**: https://platform.openai.com/docs
- **Google Gemini API**: https://ai.google.dev/docs

### 관련 프로젝트 문서
- **README.md**: 프로젝트 개요 및 아키텍처
- **FRONTEND_API_RESPONSE_FORMAT.md**: 프론트엔드 API 통합 가이드
- **db_api_docs.txt**: 백엔드 DB API 문서

### 커뮤니티 지원
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discord**: 실시간 기술 지원 (링크 추가 필요)

---

**문서 작성**: 2025-11-20
**마지막 업데이트**: 2025-11-20
**작성자**: PQC Inspector Team

**질문이나 문제가 있으신가요? GitHub Issues를 통해 문의해주세요!**
