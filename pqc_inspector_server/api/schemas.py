# File: pqc_inspector_server/api/schemas.py
# 📜 API의 요청(Request)과 응답(Response) 데이터 형식을 Pydantic 모델로 정의하는 파일입니다.
# FastAPI는 이 모델들을 사용하여 데이터 검증, 직렬화, 그리고 API 문서를 자동으로 생성합니다.

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# --- 분석 결과 스키마 ---
class AnalysisResultBase(BaseModel):
    file_name: str = Field(..., description="분석된 파일의 원본 이름")
    file_type: str = Field(..., description="오케스트레이터가 분류한 파일 타입 (e.g., source_code, binary)")
    is_pqc_vulnerable: bool = Field(..., description="비양자내성암호 사용 여부")
    vulnerability_details: Optional[str] = Field(None, description="발견된 취약점 상세 설명")
    detected_algorithms: Optional[List[str]] = Field(default_factory=list, description="탐지된 암호화 알고리즘 목록")
    recommendations: Optional[str] = Field(None, description="PQC 전환 권장사항")
    evidence: Optional[str] = Field(None, description="탐지의 근거가 되는 코드 라인 또는 문자열")
    confidence_score: Optional[float] = Field(None, description="탐지 결과에 대한 신뢰도 점수 (0.0 ~ 1.0)", ge=0.0, le=1.0)
    orchestrator_summary: Optional[str] = Field(None, description="오케스트레이터 AI의 종합 검증 의견")

class AnalysisResultCreate(AnalysisResultBase):
    # 외부 API에 저장 시 필요한 데이터
    pass

class AnalysisResultSchema(AnalysisResultBase):
    # API 응답 시 클라이언트에게 보여줄 데이터
    task_id: str = Field(..., description="분석 작업 ID")
    analysis_timestamp: str = Field(..., description="분석 완료 시간")

    class Config:
        from_attributes = True

# --- 분석 요청 응답 스키마 ---
class AnalysisRequestResponse(BaseModel):
    task_id: str = Field(..., description="백그라운드에서 실행될 분석 작업의 고유 ID")
    message: str = Field(..., description="요청 접수 완료 메시지")

# --- 에이전트 응답 스키마 ---
class AgentAnalysisResult(BaseModel):
    is_pqc_vulnerable: bool = Field(..., description="비양자내성암호 사용 여부")
    vulnerability_details: Optional[str] = Field(None, description="발견된 취약점 상세 설명")
    detected_algorithms: Optional[List[str]] = Field(default_factory=list, description="탐지된 암호화 알고리즘 목록")
    recommendations: Optional[str] = Field(None, description="PQC 전환 권장사항")
    evidence: Optional[str] = Field(None, description="탐지의 근거")
    confidence_score: Optional[float] = Field(0.0, description="신뢰도 점수", ge=0.0, le=1.0)
    orchestrator_summary: Optional[str] = Field(None, description="오케스트레이터 검증 의견")

# --- 오류 응답 스키마 ---
class ErrorResponse(BaseModel):
    error: str = Field(..., description="오류 메시지")
    detail: Optional[str] = Field(None, description="오류 상세 정보")
    task_id: Optional[str] = Field(None, description="관련 작업 ID")
