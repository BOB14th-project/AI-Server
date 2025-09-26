# File: pqc_inspector_server/db/api_client.py
# 💾 외부 API와 통신하는 클라이언트입니다.

import httpx
import asyncio
from typing import Dict, Any, Optional
from ..core.config import settings

class ExternalAPIClient:
    def __init__(self):
        self.base_url = settings.EXTERNAL_API_BASE_URL
        self.api_key = settings.EXTERNAL_API_KEY
        self.timeout = settings.EXTERNAL_API_TIMEOUT
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        print("ExternalAPIClient가 초기화되었습니다.")

    async def save_analysis_result(self, task_id: str, result_data: Dict[str, Any]) -> bool:
        """
        분석 결과를 외부 API를 통해 저장합니다.
        테스트용으로 JSONPlaceholder API를 사용합니다.
        """
        try:
            # JSONPlaceholder의 posts 엔드포인트를 사용하여 테스트
            payload = {
                "title": f"PQC Analysis Result - {task_id}",
                "body": str(result_data),
                "userId": 1
            }
            response = await self.client.post("/posts", json=payload)
            response.raise_for_status()
            print(f"작업 ID [{task_id}] - 외부 API에 결과 저장 성공 (테스트)")
            return True
        except httpx.HTTPStatusError as e:
            print(f"외부 API 오류 (저장): {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"외부 API 연결 오류 (저장): {e}")
            return False

    async def get_analysis_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        주어진 작업 ID의 분석 결과를 외부 API에서 조회합니다.
        테스트용으로 JSONPlaceholder API를 사용합니다.
        """
        try:
            # 테스트용으로 posts/1을 조회하고 task_id를 시뮬레이션
            response = await self.client.get("/posts/1")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            
            # 실제 결과를 시뮬레이션
            mock_result = {
                "task_id": task_id,
                "file_name": "test_file.py",
                "file_type": "source_code",
                "is_pqc_vulnerable": True,
                "vulnerability_details": "발견된 비양자내성암호: RSA 2048",
                "recommendations": "CRYSTALS-Kyber로 교체 권장",
                "confidence_score": 0.95,
                "analysis_timestamp": "2024-01-01T00:00:00Z"
            }
            
            print(f"작업 ID [{task_id}] - 외부 API에서 결과 조회 성공 (테스트)")
            return mock_result
        except httpx.HTTPStatusError as e:
            print(f"외부 API 오류 (조회): {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"외부 API 연결 오류 (조회): {e}")
            return None

    async def close(self):
        """클라이언트 연결을 종료합니다."""
        await self.client.aclose()

# 의존성 주입을 위한 함수
def get_api_client():
    return ExternalAPIClient()
