#!/usr/bin/env python3
"""Binary 에이전트의 벡터 DB 재구성 스크립트"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pqc_inspector_server.services.vector_store import VectorStoreFactory
from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def rebuild_binary_vector_db():
    """Binary 에이전트의 벡터 DB를 재구성합니다."""

    print("🔄 Binary 에이전트 벡터 DB 재구성 시작...\n")

    # 1. VectorStore 가져오기
    vector_store = VectorStoreFactory.get_store("assembly_binary")

    # 2. 기존 컬렉션 삭제
    print("🗑️ 기존 벡터 DB 삭제 중...")
    vector_store.clear_collection()
    print("✅ 삭제 완료\n")

    # 3. KnowledgeManager로 재초기화
    print("📚 지식 베이스 재로드 중...")
    km = await KnowledgeManagerFactory.get_manager("assembly_binary")

    # 강제 재로드
    await km.initialize_knowledge_base(force_reload=True)

    # 4. 결과 확인
    collection_info = vector_store.get_collection_info()
    print(f"\n✅ 재구성 완료!")
    print(f"   총 문서 수: {collection_info['document_count']}개")
    print(f"   컬렉션 이름: {collection_info['collection_name']}")

if __name__ == "__main__":
    asyncio.run(rebuild_binary_vector_db())
