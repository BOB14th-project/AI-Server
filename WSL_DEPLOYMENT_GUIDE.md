# 🪟 PQC Inspector AI Server - WSL 배포 가이드

**Windows 환경에서 WSL(Windows Subsystem for Linux)을 사용한 배포 가이드**

**최종 업데이트**: 2025-11-20

---

## 📋 목차

1. [WSL이란?](#1-wsl이란)
2. [WSL 설치 및 설정](#2-wsl-설치-및-설정)
3. [AI 서버 설치 (WSL 환경)](#3-ai-서버-설치-wsl-환경)
4. [ngrok으로 외부 접근 설정](#4-ngrok으로-외부-접근-설정)
5. [WSL 특수 상황 처리](#5-wsl-특수-상황-처리)
6. [문제 해결](#6-문제-해결)

---

## 1. WSL이란?

**WSL (Windows Subsystem for Linux)**는 Windows에서 Linux 환경을 네이티브로 실행할 수 있게 해주는 기술입니다.

### 장점
- ✅ Windows에서 Linux 명령어 그대로 사용 가능
- ✅ 듀얼 부팅 없이 Linux 환경 실행
- ✅ Windows와 파일 시스템 공유 가능
- ✅ 높은 성능 (WSL 2는 실제 Linux 커널 사용)

### AI 서버에 WSL을 사용하는 이유
- 🐧 Linux 환경이 Python/AI 개발에 최적화
- 📦 패키지 설치가 더 안정적
- 🔧 systemd 등 Linux 도구 사용 가능
- 🚀 성능이 네이티브 Windows보다 우수

---

## 2. WSL 설치 및 설정

### 2.1 WSL 설치 (Windows 10/11)

#### 자동 설치 (권장)

**PowerShell을 관리자 권한으로 실행**:
```powershell
# WSL 설치 (Ubuntu 22.04 LTS)
wsl --install -d Ubuntu-22.04
```

**재부팅 후 Ubuntu 터미널 실행**:
- 시작 메뉴 → Ubuntu 검색

**첫 실행 시 사용자 설정**:
```
Enter new UNIX username: your_username
New password: ****
Retype new password: ****
```

#### 수동 설치 (Windows 10 이전 버전)

**PowerShell (관리자)**:
```powershell
# 1. WSL 기능 활성화
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 2. Virtual Machine Platform 활성화 (WSL 2용)
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 3. 재부팅
Restart-Computer

# 4. WSL 2를 기본값으로 설정
wsl --set-default-version 2

# 5. Microsoft Store에서 Ubuntu 22.04 설치
```

### 2.2 WSL 버전 확인

```powershell
# PowerShell에서 실행
wsl --list --verbose
```

**출력 예시**:
```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
```

**VERSION이 2여야 최적 성능입니다!**

### 2.3 WSL 기본 설정

#### 메모리 제한 설정 (선택사항)

**`C:\Users\YourName\.wslconfig` 파일 생성**:
```ini
[wsl2]
memory=8GB          # WSL에 할당할 최대 메모리
processors=4        # WSL에 할당할 CPU 코어 수
swap=2GB            # 스왑 메모리
```

**WSL 재시작**:
```powershell
# PowerShell에서
wsl --shutdown
# Ubuntu 터미널 다시 실행
```

---

## 3. AI 서버 설치 (WSL 환경)

### 3.1 WSL Ubuntu 터미널에서 시작

**Windows 시작 메뉴 → Ubuntu 실행**

### 3.2 시스템 업데이트

```bash
# 패키지 목록 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 도구 설치
sudo apt install -y build-essential git curl wget
```

### 3.3 Python 설치

```bash
# Python 3.13 설치 (Ubuntu 22.04)
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev

# Python 버전 확인
python3.13 --version
# 출력: Python 3.13.0

# pip 설치
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13

# 심볼릭 링크 생성 (선택사항)
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1
```

### 3.4 프로젝트 클론 및 설치

#### 방법 1: WSL 파일 시스템에 클론 (권장)

```bash
# WSL 홈 디렉토리에서 작업
cd ~

# Git 설치 확인
git --version

# 프로젝트 클론
git clone https://github.com/your-org/AI-Server.git
cd AI-Server

# 가상환경 생성
python3.13 -m venv .venv

# 가상환경 활성화
source .venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 패키지 설치 (5-10분 소요)
pip install -r requirements.txt
```

#### 방법 2: Windows 파일 시스템 사용 (선택사항)

```bash
# Windows C 드라이브 접근: /mnt/c/
cd /mnt/c/Users/YourName/Projects/

# 프로젝트 클론
git clone https://github.com/your-org/AI-Server.git
cd AI-Server

# 이후 동일...
```

**⚠️ 주의**: Windows 파일 시스템(`/mnt/c/`)은 성능이 느릴 수 있습니다. WSL 파일 시스템(`~/`)을 권장합니다.

### 3.5 환경 변수 설정

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

**저장**: `Ctrl + X` → `Y` → `Enter`

### 3.6 서버 실행

```bash
# 가상환경 활성화 확인
source .venv/bin/activate

# 서버 실행
python main.py
```

**출력**:
```
PQC Inspector 서버를 시작합니다.
API 문서(Swagger UI): http://127.0.0.1:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3.7 서버 테스트

**새 WSL 터미널 열기** (Windows Terminal 사용 권장):
```bash
curl http://127.0.0.1:8000/
# 출력: {"message":"PQC Inspector 서버가 정상적으로 실행 중입니다!"}
```

**또는 Windows 브라우저에서**:
```
http://localhost:8000/docs
```

---

## 4. ngrok으로 외부 접근 설정

### 4.1 ngrok 설치 (WSL 환경)

```bash
# ngrok Linux 버전 다운로드
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# 압축 해제
tar -xvzf ngrok-v3-stable-linux-amd64.tgz

# 실행 파일 이동
sudo mv ngrok /usr/local/bin/

# 설치 확인
ngrok version
# 출력: ngrok version 3.x.x
```

### 4.2 ngrok 인증

```bash
# 1. https://dashboard.ngrok.com/signup 에서 회원가입
# 2. https://dashboard.ngrok.com/get-started/your-authtoken 에서 토큰 복사
# 3. WSL에서 인증
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### 4.3 터널 시작

**WSL 터미널 1 - AI 서버**:
```bash
cd ~/AI-Server
source .venv/bin/activate
python main.py
```

**WSL 터미널 2 - ngrok**:
```bash
ngrok http 8000
```

**또는 Windows Terminal에서 새 탭으로 열기**:
```
Windows Terminal → 새 탭 → Ubuntu 선택
```

### 4.4 ngrok URL 확인

```
ngrok

Forwarding    https://1a2b-3c4d-5e6f.ngrok-free.app -> http://localhost:8000
```

**이 URL을 프론트엔드 개발자에게 공유!**

### 4.5 외부에서 테스트

```bash
# 다른 컴퓨터에서
curl https://1a2b-3c4d-5e6f.ngrok-free.app/

# Windows PowerShell에서도 테스트 가능
Invoke-WebRequest -Uri https://1a2b-3c4d-5e6f.ngrok-free.app/
```

---

## 5. WSL 특수 상황 처리

### 5.1 WSL에서 Windows 파일 접근

```bash
# Windows C 드라이브
cd /mnt/c/

# Windows 사용자 폴더
cd /mnt/c/Users/YourName/

# D 드라이브
cd /mnt/d/
```

### 5.2 Windows에서 WSL 파일 접근

**Windows 탐색기 주소창**:
```
\\wsl$\Ubuntu-22.04\home\your_username\AI-Server
```

**또는**:
```
\\wsl.localhost\Ubuntu-22.04\home\your_username\AI-Server
```

### 5.3 WSL에서 Windows 명령 실행

```bash
# Windows의 메모장 열기
notepad.exe .env

# Windows 탐색기 열기
explorer.exe .

# PowerShell 명령 실행
powershell.exe -Command "Get-Date"
```

### 5.4 WSL과 Windows 간 복사/붙여넣기

- **복사**: WSL 터미널에서 텍스트 선택 → 자동 복사
- **붙여넣기**: `Ctrl + Shift + V` 또는 마우스 우클릭

### 5.5 백그라운드 실행 (WSL 터미널 종료 후에도 실행)

#### 방법 1: nohup 사용

```bash
cd ~/AI-Server
source .venv/bin/activate
nohup python main.py > server.log 2>&1 &

# PID 확인
ps aux | grep "python main.py"

# 로그 확인
tail -f server.log

# 서버 종료
kill <PID>
```

#### 방법 2: tmux 사용 (권장)

```bash
# tmux 설치
sudo apt install tmux

# 새 세션 시작
tmux new -s ai-server

# 서버 실행
cd ~/AI-Server
source .venv/bin/activate
python main.py

# 세션에서 나가기 (서버는 계속 실행)
Ctrl + B, 그다음 D

# 세션 다시 연결
tmux attach -t ai-server

# 세션 종료
exit
```

#### 방법 3: systemd 사용 (WSL 2.0.0+)

**WSL 버전 확인**:
```bash
wsl --version
```

**systemd 활성화**:
```bash
# /etc/wsl.conf 파일 생성
sudo nano /etc/wsl.conf
```

**파일 내용**:
```ini
[boot]
systemd=true
```

**WSL 재시작** (PowerShell에서):
```powershell
wsl --shutdown
# Ubuntu 터미널 다시 실행
```

**서비스 파일 생성**:
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

[Install]
WantedBy=multi-user.target
```

**서비스 실행**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pqc-inspector
sudo systemctl start pqc-inspector

# 상태 확인
sudo systemctl status pqc-inspector

# 로그 확인
sudo journalctl -u pqc-inspector -f
```

---

## 6. 문제 해결

### 6.1 WSL 일반 문제

#### 문제 1: WSL이 시작되지 않음

**PowerShell (관리자)**:
```powershell
# WSL 재시작
wsl --shutdown
wsl

# 또는 WSL 업데이트
wsl --update
```

#### 문제 2: 인터넷 연결 문제

```bash
# DNS 설정 확인
cat /etc/resolv.conf

# DNS 수동 설정
sudo nano /etc/resolv.conf
# 다음 추가:
# nameserver 8.8.8.8
# nameserver 1.1.1.1
```

#### 문제 3: Windows 방화벽 문제

**Windows PowerShell (관리자)**:
```powershell
# 포트 8000 허용
New-NetFirewallRule -DisplayName "AI Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### 6.2 성능 문제

#### WSL 2가 느릴 때

**원인**: Windows 파일 시스템(`/mnt/c/`) 사용

**해결**:
```bash
# WSL 파일 시스템으로 프로젝트 이동
cp -r /mnt/c/Users/YourName/AI-Server ~/
cd ~/AI-Server
```

#### 메모리 부족

**`.wslconfig` 수정** (`C:\Users\YourName\.wslconfig`):
```ini
[wsl2]
memory=8GB
```

**WSL 재시작**:
```powershell
wsl --shutdown
```

### 6.3 포트 접근 문제

#### WSL 포트가 Windows에서 접근 안 됨

**원인**: WSL 2 네트워크 격리

**해결 1: Windows에서 포트 포워딩** (PowerShell 관리자):
```powershell
# WSL IP 확인
wsl hostname -I
# 출력: 172.x.x.x

# 포트 포워딩 (8000 → WSL)
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=172.x.x.x

# 확인
netsh interface portproxy show all
```

**해결 2: localhost 사용**

WSL 2는 자동으로 `localhost`를 Windows와 공유합니다:
```bash
# WSL에서
python main.py
# 서버가 0.0.0.0:8000 또는 127.0.0.1:8000에서 실행

# Windows 브라우저에서 접근
http://localhost:8000/docs
```

### 6.4 패키지 설치 문제

#### torch 설치 실패

```bash
# CPU 버전 torch 설치
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

#### capstone 설치 실패

```bash
# 빌드 도구 설치
sudo apt install -y build-essential python3-dev

# 재설치
pip install --no-cache-dir capstone
```

---

## 7. 유용한 WSL 명령어

### WSL 관리 (PowerShell에서)

```powershell
# WSL 종료
wsl --shutdown

# 특정 배포판 종료
wsl --terminate Ubuntu-22.04

# 배포판 목록
wsl --list --verbose

# 기본 배포판 설정
wsl --set-default Ubuntu-22.04

# WSL 업데이트
wsl --update

# WSL 버전 전환 (1 ↔ 2)
wsl --set-version Ubuntu-22.04 2
```

### WSL 백업 및 복원 (PowerShell)

```powershell
# 백업 (Export)
wsl --export Ubuntu-22.04 D:\wsl-backup\ubuntu-22.04.tar

# 복원 (Import)
wsl --import Ubuntu-22.04-Restored D:\WSL\Ubuntu-Restored D:\wsl-backup\ubuntu-22.04.tar

# 배포판 삭제
wsl --unregister Ubuntu-22.04
```

---

## 8. 추천 도구

### Windows Terminal (필수!)

**설치**:
- Microsoft Store에서 "Windows Terminal" 검색 및 설치

**장점**:
- 여러 탭 지원 (PowerShell, WSL, CMD 동시 사용)
- 아름다운 UI
- GPU 가속 지원
- 복사/붙여넣기 편리

### VS Code WSL 확장

**VS Code에서 WSL 프로젝트 열기**:
```bash
# WSL 터미널에서
cd ~/AI-Server
code .
```

**VS Code 확장 설치**:
- `WSL` (Microsoft)
- `Python` (Microsoft)
- `Remote - WSL` (Microsoft)

---

## 9. 체크리스트

### WSL 설치 체크리스트

- [ ] WSL 설치 완료 (`wsl --install`)
- [ ] Ubuntu 22.04 설치 완료
- [ ] WSL 버전 2 확인
- [ ] 사용자 계정 생성 완료
- [ ] 시스템 업데이트 완료 (`sudo apt update && upgrade`)

### AI 서버 설치 체크리스트

- [ ] Python 3.13 설치 완료
- [ ] Git 설치 완료
- [ ] 프로젝트 클론 완료
- [ ] 가상환경 생성 완료
- [ ] requirements.txt 설치 완료
- [ ] .env 파일 설정 완료
- [ ] 서버 실행 테스트 성공

### ngrok 설정 체크리스트

- [ ] ngrok 설치 완료 (WSL 환경)
- [ ] ngrok 계정 생성 및 인증 완료
- [ ] ngrok 터널 실행 성공
- [ ] 외부에서 API 접근 테스트 성공
- [ ] 프론트엔드에 ngrok URL 전달 완료

---

## 10. 추가 리소스

### 공식 문서
- **WSL 문서**: https://learn.microsoft.com/en-us/windows/wsl/
- **ngrok 문서**: https://ngrok.com/docs
- **Ubuntu WSL 가이드**: https://ubuntu.com/wsl

### 관련 문서
- **SERVER_DEPLOYMENT_GUIDE.md**: 전체 배포 가이드
- **QUICK_START.md**: 빠른 시작 가이드
- **FRONTEND_API_RESPONSE_FORMAT.md**: API 통합 가이드

---

## ✅ 요약

WSL에서 AI 서버를 실행하는 것은 **Windows 네이티브보다 훨씬 안정적**입니다!

**핵심 단계**:
1. ✅ WSL 2 설치 (`wsl --install -d Ubuntu-22.04`)
2. ✅ Python 3.13 설치
3. ✅ 프로젝트 클론 및 패키지 설치
4. ✅ ngrok으로 외부 접근 설정
5. ✅ tmux 또는 systemd로 백그라운드 실행

**장점**:
- 🚀 Linux 환경에서 더 빠르고 안정적
- 🔧 systemd, tmux 등 Linux 도구 사용 가능
- 🌐 ngrok 등 외부 접근 도구와 완벽 호환
- 💾 Windows 파일과 쉽게 공유 가능

**질문이 있으신가요? GitHub Issues를 통해 문의해주세요!**

---

**문서 작성**: 2025-11-20
**마지막 업데이트**: 2025-11-20
**작성자**: PQC Inspector Team
