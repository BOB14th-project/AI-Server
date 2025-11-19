# File: pqc_inspector_server/db/api_client.py
# 💾 외부 DB API와 통신하는 클라이언트입니다.

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from ..core.config import settings

class ExternalAPIClient:
    def __init__(self):
        self.base_url = settings.EXTERNAL_API_BASE_URL
        self.timeout = settings.EXTERNAL_API_TIMEOUT
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        print("ExternalAPIClient가 초기화되었습니다.")

    async def get_llm_assembly(self, file_id: int, scan_id: int) -> Optional[str]:
        """
        DB에서 어셈블리 텍스트를 가져옵니다.
        GET /files/{file_id}/llm/?scan_id={scan_id}
        GitHub 스키마: LLMAssemblyGet { Field_text: str }
        """
        try:
            response = await self.client.get(
                f"/files/{file_id}/llm/",
                params={"scan_id": scan_id}
            )
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                # GitHub 코드에서는 Field_text를 반환
                return data[0].get("Field_text") or data[0].get("File_text")
            return None
        except httpx.HTTPStatusError as e:
            print(f"DB API 오류 (어셈블리 조회): {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"DB API 연결 오류 (어셈블리 조회): {e}")
            return None

    async def get_llm_code(self, file_id: int, scan_id: int) -> Optional[str]:
        """
        DB에서 생성된 코드를 가져옵니다.
        GET /files/{file_id}/llm_code/?scan_id={scan_id}
        """
        try:
            response = await self.client.get(
                f"/files/{file_id}/llm_code/",
                params={"scan_id": scan_id}
            )
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                return data[0].get("Code")
            return None
        except httpx.HTTPStatusError as e:
            print(f"DB API 오류 (코드 조회): {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"DB API 연결 오류 (코드 조회): {e}")
            return None

    async def get_llm_logs(self, file_id: int, scan_id: int) -> Optional[str]:
        """
        DB에서 로그를 가져옵니다.
        GET /files/{file_id}/llm_log/?scan_id={scan_id}
        """
        try:
            response = await self.client.get(
                f"/files/{file_id}/llm_log/",
                params={"scan_id": scan_id}
            )
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                return data[0].get("Log")
            return None
        except httpx.HTTPStatusError as e:
            print(f"DB API 오류 (로그 조회): {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"DB API 연결 오류 (로그 조회): {e}")
            return None

    async def get_all_file_data(self, file_id: int, scan_id: int) -> Dict[str, Any]:
        """
        DB에서 파일의 모든 데이터를 가져옵니다 (어셈블리, 코드, 로그).
        """
        print(f"파일 ID [{file_id}], 스캔 ID [{scan_id}] - DB에서 모든 데이터 조회 시작")

        # 병렬로 모든 데이터 조회
        assembly_task = self.get_llm_assembly(file_id, scan_id)
        code_task = self.get_llm_code(file_id, scan_id)
        logs_task = self.get_llm_logs(file_id, scan_id)

        assembly, code, logs = await asyncio.gather(
            assembly_task, code_task, logs_task
        )

        result = {
            "file_id": file_id,
            "scan_id": scan_id,
            "assembly_text": assembly,
            "generated_code": code,
            "logs": logs
        }

        print(f"DB 데이터 조회 완료 - 어셈블리: {bool(assembly)}, 코드: {bool(code)}, 로그: {bool(logs)}")
        return result

    async def save_llm_assembly(self, file_id: int, scan_id: int, file_text: str) -> Optional[int]:
        """
        어셈블리 텍스트를 DB에 저장합니다.
        POST /files/{file_id}/llm/
        """
        try:
            payload = {
                "File_id": file_id,
                "Scan_id": scan_id,
                "File_text": file_text
            }
            response = await self.client.post(
                f"/files/{file_id}/llm/",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            analysis_id = data.get("Analysis_id")
            print(f"어셈블리 텍스트 저장 성공 - Analysis_id: {analysis_id}")
            return analysis_id
        except httpx.HTTPStatusError as e:
            print(f"DB API 오류 (어셈블리 저장): {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"DB API 연결 오류 (어셈블리 저장): {e}")
            return None

    async def save_llm_analysis(self, file_id: int, scan_id: int, llm_analysis: str) -> bool:
        """
        LLM 분석 결과를 DB에 저장합니다.
        POST /files/{file_id}/llm_analysis/
        """
        try:
            payload = {
                "File_id": file_id,
                "Scan_id": scan_id,
                "LLM_analysis": llm_analysis
            }
            response = await self.client.post(
                f"/files/{file_id}/llm_analysis/",
                json=payload
            )
            response.raise_for_status()
            print(f"LLM 분석 결과 저장 성공 - File_id: {file_id}, Scan_id: {scan_id}")
            return True
        except httpx.HTTPStatusError as e:
            print(f"DB API 오류 (분석 결과 저장): {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"DB API 연결 오류 (분석 결과 저장): {e}")
            return False

    async def save_llm_code(self, file_id: int, scan_id: int, code: str) -> bool:
        """
        생성된 코드를 DB에 저장합니다.
        POST /files/{file_id}/llm_code/
        """
        try:
            payload = {
                "File_id": file_id,
                "Scan_id": scan_id,
                "Code": code
            }
            response = await self.client.post(
                f"/files/{file_id}/llm_code/",
                json=payload
            )
            response.raise_for_status()
            print(f"생성 코드 저장 성공 - File_id: {file_id}, Scan_id: {scan_id}")
            return True
        except httpx.HTTPStatusError as e:
            print(f"DB API 오류 (코드 저장): {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"DB API 연결 오류 (코드 저장): {e}")
            return False

    async def save_llm_log(self, file_id: int, scan_id: int, log: str) -> bool:
        """
        로그를 DB에 저장합니다.
        POST /files/{file_id}/llm_log/
        """
        try:
            payload = {
                "File_id": file_id,
                "Scan_id": scan_id,
                "Log": log
            }
            response = await self.client.post(
                f"/files/{file_id}/llm_log/",
                json=payload
            )
            response.raise_for_status()
            print(f"로그 저장 성공 - File_id: {file_id}, Scan_id: {scan_id}")
            return True
        except httpx.HTTPStatusError as e:
            print(f"DB API 오류 (로그 저장): {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"DB API 연결 오류 (로그 저장): {e}")
            return False

    async def close(self):
        """클라이언트 연결을 종료합니다."""
        await self.client.aclose()

# 의존성 주입을 위한 함수
def get_api_client():
    return ExternalAPIClient()
