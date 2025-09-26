# File: pqc_inspector_server/services/vector_store.py
# 🗄️ ChromaDB를 사용한 벡터 데이터베이스 서비스입니다.

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
import os
from ..core.config import settings as app_settings

class VectorStore:
    def __init__(self, collection_name: str, persist_directory: str = None):
        self.collection_name = collection_name

        # 영구 저장 디렉토리 설정
        if persist_directory is None:
            persist_directory = os.path.join(os.getcwd(), "data", "vector_db")

        os.makedirs(persist_directory, exist_ok=True)

        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # 컬렉션 생성 또는 가져오기
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"✅ 기존 컬렉션 '{collection_name}' 로드됨")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": f"PQC Inspector {collection_name} knowledge base"}
            )
            print(f"✅ 새 컬렉션 '{collection_name}' 생성됨")

    async def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        문서들을 벡터 데이터베이스에 추가합니다.
        """
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]

            print(f"📚 벡터 DB에 {len(documents)}개 문서 추가 중...")

            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            print(f"✅ {len(documents)}개 문서가 '{self.collection_name}' 컬렉션에 추가됨")
            return True

        except Exception as e:
            print(f"❌ 문서 추가 중 오류: {e}")
            return False

    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        쿼리와 유사한 문서들을 검색합니다.
        """
        try:
            print(f"🔍 벡터 유사도 검색 시작 (top_k={top_k})")

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )

            search_results = {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "ids": results["ids"][0] if results["ids"] else []
            }

            print(f"✅ {len(search_results['documents'])}개 관련 문서 발견")
            return search_results

        except Exception as e:
            print(f"❌ 벡터 검색 중 오류: {e}")
            return {"documents": [], "metadatas": [], "distances": [], "ids": []}

    def get_collection_info(self) -> Dict[str, Any]:
        """
        컬렉션 정보를 반환합니다.
        """
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "document_count": count,
                "status": "active"
            }
        except Exception as e:
            return {
                "name": self.collection_name,
                "document_count": 0,
                "status": f"error: {e}"
            }

    def clear_collection(self) -> bool:
        """
        컬렉션의 모든 데이터를 삭제합니다.
        """
        try:
            # 모든 문서 ID 가져오기
            all_results = self.collection.get()
            if all_results["ids"]:
                self.collection.delete(ids=all_results["ids"])
                print(f"✅ 컬렉션 '{self.collection_name}' 초기화 완료")
            return True
        except Exception as e:
            print(f"❌ 컬렉션 초기화 중 오류: {e}")
            return False

# 각 에이전트별 벡터 스토어 팩토리
class VectorStoreFactory:
    _instances = {}

    @classmethod
    def get_store(cls, agent_type: str) -> VectorStore:
        """
        에이전트 타입별 벡터 스토어 인스턴스를 반환합니다.
        """
        if agent_type not in cls._instances:
            collection_name = f"pqc_inspector_{agent_type}"
            cls._instances[agent_type] = VectorStore(collection_name)

        return cls._instances[agent_type]

# 의존성 주입을 위한 함수들
def get_source_code_vector_store() -> VectorStore:
    return VectorStoreFactory.get_store("source_code")

def get_binary_vector_store() -> VectorStore:
    return VectorStoreFactory.get_store("binary")

def get_parameter_vector_store() -> VectorStore:
    return VectorStoreFactory.get_store("parameter")

def get_log_conf_vector_store() -> VectorStore:
    return VectorStoreFactory.get_store("log_conf")