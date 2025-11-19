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


@api_router.post("/analyze/db")
async def analyze_from_database(
    file_id: int,
    scan_id: int,
    orchestrator: OrchestratorController = Depends(get_orchestrator_controller)
):
    """
    DB에서 파일 데이터를 가져와 종합 분석을 수행하고 결과를 DB에 저장합니다.

    Parameters:
    - file_id: 분석할 파일의 ID
    - scan_id: 스캔 세션 ID

    Returns:
    - 분석 성공 여부 및 결과
    """
    result = await orchestrator.analyze_from_db(file_id, scan_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "분석 실패")
        )

    return {
        "message": "분석이 성공적으로 완료되었습니다.",
        "file_id": file_id,
        "scan_id": scan_id,
        "analysis_preview": result.get("analysis_preview", "")
    }


@api_router.post("/analyze/db/all")
async def analyze_all_files_from_database(
    scan_id: int,
    max_files: int = 100,
    orchestrator: OrchestratorController = Depends(get_orchestrator_controller)
):
    """
    DB에 있는 모든 파일을 자동으로 검사합니다.

    Parameters:
    - scan_id: 스캔 세션 ID
    - max_files: 최대 검사할 파일 개수 (기본값: 100)

    Returns:
    - 전체 분석 결과 요약
    """
    result = await orchestrator.analyze_all_files_from_db(scan_id, max_files)

    return {
        "message": "전체 파일 분석이 완료되었습니다.",
        "scan_id": scan_id,
        "total_attempted": result.get("total_attempted", 0),
        "total_success": result.get("total_success", 0),
        "total_failed": result.get("total_failed", 0),
        "results": result.get("results", [])
    }


# --- 에이전트별 직접 분석 엔드포인트 (벤치마크용) ---
from .schemas import AgentAnalysisResult
from ..agents.source_code import SourceCodeAgent
from ..agents.assembly_binary import AssemblyBinaryAgent
from ..agents.logs_config import LogsConfigAgent


@api_router.post("/analyze/source_code", response_model=AgentAnalysisResult)
async def analyze_with_source_code_agent(
    file: UploadFile = File(...)
):
    """
    SourceCodeAgent를 직접 호출하여 소스코드 파일을 분석합니다.
    오케스트레이터를 거치지 않고 순수 에이전트 성능을 측정할 수 있습니다.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일 이름이 없습니다.")

    try:
        file_content = await file.read()
        agent = SourceCodeAgent()
        result = await agent.analyze(file_content, file.filename)
        return AgentAnalysisResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")


@api_router.post("/analyze/assembly_binary", response_model=AgentAnalysisResult)
async def analyze_with_assembly_binary_agent(
    file: UploadFile = File(...)
):
    """
    AssemblyBinaryAgent를 직접 호출하여 어셈블리/바이너리 파일을 분석합니다.
    오케스트레이터를 거치지 않고 순수 에이전트 성능을 측정할 수 있습니다.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일 이름이 없습니다.")

    try:
        file_content = await file.read()
        agent = AssemblyBinaryAgent()
        result = await agent.analyze(file_content, file.filename)
        return AgentAnalysisResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")


@api_router.post("/analyze/logs_config", response_model=AgentAnalysisResult)
async def analyze_with_logs_config_agent(
    file: UploadFile = File(...)
):
    """
    LogsConfigAgent를 직접 호출하여 로그/설정 파일을 분석합니다.
    오케스트레이터를 거치지 않고 순수 에이전트 성능을 측정할 수 있습니다.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일 이름이 없습니다.")

    try:
        file_content = await file.read()
        agent = LogsConfigAgent()
        result = await agent.analyze(file_content, file.filename)

        # 결과 로깅
        print(f"   📊 에이전트 분석 결과: {result}")

        # Pydantic 검증 시도
        try:
            validated_result = AgentAnalysisResult(**result)
            print(f"   ✅ Pydantic 검증 성공")
            return validated_result
        except Exception as validation_error:
            print(f"   ❌ Pydantic 검증 실패: {validation_error}")
            print(f"   📄 문제 필드: {result.keys()}")
            raise

    except HTTPException:
        # HTTPException은 그대로 전파
        raise
    except Exception as e:
        import traceback
        print(f"   ❌ 전체 에러 스택:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")
