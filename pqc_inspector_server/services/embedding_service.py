# File: pqc_inspector_server/services/embedding_service.py
# 🧠 텍스트/코드를 벡터로 변환하는 임베딩 서비스입니다.

import httpx
from typing import List, Dict, Any
from ..core.config import settings

class EmbeddingService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_base_url = "https://api.openai.com/v1"
        self.embedding_model = "text-embedding-3-small"  # OpenAI 최신 임베딩 모델
        print("EmbeddingService가 초기화되었습니다.")

    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        텍스트 목록을 임베딩 벡터로 변환합니다.
        """
        try:
            print(f"🧠 임베딩 생성 시작: {len(texts)}개 텍스트")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.openai_base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.embedding_model,
                        "input": texts
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    embeddings = [item["embedding"] for item in data["data"]]
                    print(f"✅ 임베딩 생성 완료: {len(embeddings)}개 벡터")
                    return embeddings
                else:
                    print(f"❌ OpenAI 임베딩 API 오류: {response.status_code} - {response.text}")
                    return []

        except Exception as e:
            print(f"❌ 임베딩 생성 중 오류: {e}")
            return []

    async def create_single_embedding(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩 벡터로 변환합니다.
        """
        embeddings = await self.create_embeddings([text])
        return embeddings[0] if embeddings else []

    def preprocess_code(self, code: str) -> str:
        """
        코드를 임베딩에 적합하게 전처리합니다.
        """
        # 주석 제거 (단순화)
        lines = []
        for line in code.split('\n'):
            # Python, Java, C++ 스타일 주석 제거
            if '//' in line:
                line = line.split('//')[0]
            if '#' in line:
                line = line.split('#')[0]
            line = line.strip()
            if line:
                lines.append(line)

        return '\n'.join(lines)

    def preprocess_config(self, config: str) -> str:
        """
        설정 파일을 임베딩에 적합하게 전처리합니다.
        """
        # JSON/YAML 키-값 쌍 추출에 집중
        import re

        # 키-값 패턴 추출
        key_value_patterns = re.findall(r'["\']?([a-zA-Z_][a-zA-Z0-9_]*)["\']?\s*[:=]\s*["\']?([^"\n\r,}]+)["\']?', config)

        processed_lines = []
        for key, value in key_value_patterns:
            processed_lines.append(f"{key}: {value}")

        return '\n'.join(processed_lines) if processed_lines else config

# 의존성 주입을 위한 함수
def get_embedding_service():
    return EmbeddingService()