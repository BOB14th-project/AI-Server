# File: pqc_inspector_server/api/endpoints.py
# 🌐 사용자의 HTTP 요청을 처리하는 API 엔드포인트를 정의하는 파일입니다.
# FastAPI의 APIRouter를 사용하여 관련 엔드포인트들을 그룹화합니다.

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from typing import Annotated
import uuid

from .schemas import AnalysisRequestResponse, AnalysisResultSchema
from ..orchestrator.controller import OrchestratorController, get_orchestrator_controller

# API 라우터 객체 생성
api_router = APIRouter()

# --- 엔드포인트 정의 ---
@api_router.post("/analyze", response_model=AnalysisRequestResponse, status_code=202)
async def analyze_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    orchestrator: OrchestratorController = Depends(get_orchestrator_controller)
):
    """
    파일을 업로드하여 비양자내성암호(Non-PQC) 사용 여부 분석을 요청합니다.
    
    분석은 백그라운드에서 처리되며, 요청 즉시 작업 ID를 반환합니다.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일 이름이 없습니다.")

    task_id = str(uuid.uuid4())
    
    # 파일 내용을 미리 읽어서 백그라운드 태스크에 전달
    file_content = await file.read()
    filename = file.filename
    
    # 실제 분석 작업은 백그라운드에서 실행하여 응답 시간을 단축합니다.
    background_tasks.add_task(orchestrator.start_analysis_with_content, filename, file_content, task_id)
    
    return {"task_id": task_id, "message": "파일 분석 요청이 성공적으로 접수되었습니다. 백그라운드에서 분석이 진행됩니다."}


@api_router.get("/report/{task_id}", response_model=AnalysisResultSchema)
async def get_analysis_report(
    task_id: str,
    orchestrator: OrchestratorController = Depends(get_orchestrator_controller)
):
    """
    주어진 작업 ID(task_id)에 해당하는 분석 결과를 조회합니다.
    """
    result = await orchestrator.get_analysis_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="해당 ID의 분석 결과를 찾을 수 없거나, 아직 분석이 진행 중입니다.")
    
    return result
