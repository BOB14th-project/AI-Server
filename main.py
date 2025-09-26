# File: main.py
# 🚀 PQC Inspector 애플리케이션을 시작하기 위한 최상위 진입점(Entrypoint) 파일입니다.
# 이 파일을 직접 실행하면 웹 서버가 구동됩니다.

import uvicorn
from fastapi import FastAPI
from pqc_inspector_server.core.config import settings
from pqc_inspector_server.api.endpoints import api_router

# 1. FastAPI 애플리케이션 객체 생성
# 이 'app' 객체가 전체 웹 애플리케이션의 중심이 됩니다.
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="비양자내성암호(Non-PQC) 탐지를 위한 AI 기반 분석 서버",
    version="0.1.0"
)

# 2. 루트(Root) 엔드포인트 정의
# 서버가 정상적으로 실행 중인지 확인하기 위한 간단한 경로입니다.
# 웹 브라우저에서 http://127.0.0.1:8000 로 접속하면 이 메시지를 볼 수 있습니다.
@app.get("/", tags=["Status"])
def read_root():
    """서버의 상태를 확인하는 기본 엔드포인트입니다."""
    return {"message": "PQC Inspector 서버가 정상적으로 실행 중입니다!"}


# 3. API 라우터(Router) 등록
# pqc_inspector_server/api/endpoints.py 파일에 정의된 모든 API 경로들을
# '/api/v1' 이라는 접두사(prefix)와 함께 애플리케이션에 포함시킵니다.
# 예: /analyze -> /api/v1/analyze
app.include_router(api_router, prefix=settings.API_V1_STR)


# 4. 서버 실행을 위한 메인 블록
# 'python main.py' 명령어로 이 파일을 직접 실행했을 때만 아래 코드가 동작합니다.
if __name__ == "__main__":
    print("PQC Inspector 서버를 시작합니다.")
    print(f"API 문서(Swagger UI): http://127.0.0.1:{settings.SERVER_PORT}/docs")
    
    # Uvicorn을 사용하여 FastAPI 앱을 실행합니다.
    uvicorn.run(
        "main:app",                      # 실행할 대상: 'main.py' 파일의 'app' 객체
        host=settings.SERVER_HOST,       # 서버 호스트 주소 (e.g., "127.0.0.1")
        port=settings.SERVER_PORT,       # 서버 포트 번호 (e.g., 8000)
        reload=True                      # 소스 코드가 변경될 때마다 서버를 자동으로 재시작합니다.
    )

      