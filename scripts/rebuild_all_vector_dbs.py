#!/usr/bin/env python3
"""모든 에이전트의 벡터 DB를 재구성하는 스크립트"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pqc_inspector_server.services.vector_store import VectorStoreFactory
from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def rebuild_vector_db(agent_type: str):
    """특정 에이전트의 벡터 DB를 재구성합니다."""

    print(f"\n{'='*80}")
    print(f"🔄 {agent_type.upper()} 에이전트 벡터 DB 재구성 시작")
    print(f"{'='*80}\n")

    try:
        # 1. VectorStore 가져오기
        vector_store = VectorStoreFactory.get_store(agent_type)

        # 2. 기존 컬렉션 삭제
        print("🗑️ 기존 벡터 DB 삭제 중...")
        vector_store.clear_collection()
        print("✅ 삭제 완료\n")

        # 3. KnowledgeManager로 재초기화 (common 디렉토리 포함)
        print("📚 지식 베이스 재로드 중 (에이전트별 + common)...")

        # 기존 캐시 삭제
        if agent_type in KnowledgeManagerFactory._instances:
            del KnowledgeManagerFactory._instances[agent_type]

        km = await KnowledgeManagerFactory.get_manager(agent_type)

        # 강제 재로드
        await km.initialize_knowledge_base(force_reload=True)

        # 4. 결과 확인
        collection_info = vector_store.get_collection_info()
        print(f"\n✅ {agent_type.upper()} 재구성 완료!")
        print(f"   총 문서 수: {collection_info['document_count']}개")

        return collection_info['document_count']

    except Exception as e:
        print(f"❌ {agent_type} 재구성 실패: {e}")
        import traceback
        traceback.print_exc()
        return 0

async def main():
    """모든 에이전트의 벡터 DB를 재구성합니다."""

    print("\n" + "🚀 " * 20)
    print("모든 에이전트 벡터 DB 재구성 시작")
    print("🚀 " * 20 + "\n")

    agents = ["source_code", "assembly_binary", "logs_config"]
    results = {}

    for agent_type in agents:
        doc_count = await rebuild_vector_db(agent_type)
        results[agent_type] = doc_count

    print("\n" + "=" * 80)
    print("📊 재구성 결과 요약")
    print("=" * 80)

    for agent_type, doc_count in results.items():
        print(f"   {agent_type:20} : {doc_count:3}개 문서")

    print("\n" + "✅ " * 20)
    print("모든 벡터 DB 재구성 완료!")
    print("✅ " * 20 + "\n")

    print("📋 변경사항:")
    print("   - common 디렉토리의 RSA, ECDSA 상세 구조 추가됨")
    print("   - detailed_structure 형식 JSON 파싱 지원")
    print("   - logs/config 에이전트 RAG 재활성화 (임계값 0.20)")
    print("\n🎯 다음 단계: 벤치마크 테스트 실행하여 성능 개선 확인\n")

if __name__ == "__main__":
    asyncio.run(main())
