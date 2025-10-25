#!/usr/bin/env python3
"""
RAG 데이터 관리 스크립트
사용법: python scripts/manage_rag_data.py [command] [options]
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory
from pqc_inspector_server.services.vector_store import VectorStoreFactory

class RAGDataManager:
    def __init__(self):
        self.knowledge_base_path = project_root / "data" / "rag_knowledge_base"
        self.agent_types = ["source_code", "binary", "log_conf"]

    async def load_json_files(self, agent_type: str) -> List[Dict[str, Any]]:
        """지정된 에이전트 타입의 모든 JSON 파일을 로드합니다."""
        agent_path = self.knowledge_base_path / agent_type

        if not agent_path.exists():
            print(f"⚠️ 경로가 존재하지 않습니다: {agent_path}")
            return []

        all_data = []

        for json_file in agent_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 데이터 구조에 따라 처리
                if 'patterns' in data:
                    all_data.extend(data['patterns'])
                elif 'signatures' in data:
                    all_data.extend(data['signatures'])
                elif 'config_patterns' in data:
                    all_data.extend(data['config_patterns'])
                elif 'log_patterns' in data:
                    all_data.extend(data['log_patterns'])
                else:
                    # 직접 배열인 경우
                    if isinstance(data, list):
                        all_data.extend(data)
                    else:
                        all_data.append(data)

                print(f"✅ 로드됨: {json_file.name}")

            except Exception as e:
                print(f"❌ {json_file.name} 로드 실패: {e}")

        return all_data

    async def refresh_knowledge_base(self, agent_type: str = None):
        """지식 베이스를 새로고침합니다."""
        agent_types = [agent_type] if agent_type else self.agent_types

        for atype in agent_types:
            print(f"\n🔄 {atype} 지식 베이스 새로고침 중...")

            try:
                manager = await KnowledgeManagerFactory.get_manager(atype)
                success = await manager.initialize_knowledge_base(force_reload=True)

                if success:
                    collection_info = manager.vector_store.get_collection_info()
                    print(f"✅ {atype}: {collection_info['document_count']}개 문서 로드됨")
                else:
                    print(f"❌ {atype}: 새로고침 실패")

            except Exception as e:
                print(f"❌ {atype} 새로고침 중 오류: {e}")

    async def show_status(self):
        """모든 지식 베이스 상태를 표시합니다."""
        print("\n📊 RAG 시스템 상태")
        print("=" * 50)

        for agent_type in self.agent_types:
            try:
                # 벡터 스토어 정보
                store = VectorStoreFactory.get_store(agent_type)
                info = store.get_collection_info()

                # JSON 파일 정보
                json_data = await self.load_json_files(agent_type)

                print(f"\n🤖 {agent_type.upper()}")
                print(f"  벡터 DB 문서 수: {info['document_count']}")
                print(f"  JSON 파일 패턴 수: {len(json_data)}")
                print(f"  상태: {info['status']}")

                # 카테고리별 통계
                if json_data:
                    categories = {}
                    for item in json_data:
                        cat = item.get('category', 'unknown')
                        categories[cat] = categories.get(cat, 0) + 1

                    print(f"  카테고리: {dict(list(categories.items())[:3])}...")

            except Exception as e:
                print(f"  ❌ 오류: {e}")

    async def test_search(self, agent_type: str, query: str):
        """특정 에이전트의 검색 기능을 테스트합니다."""
        print(f"\n🧪 {agent_type} 검색 테스트")
        print(f"쿼리: {query}")
        print("-" * 40)

        try:
            manager = await KnowledgeManagerFactory.get_manager(agent_type)
            result = await manager.search_relevant_context(query, top_k=3)

            print(f"평균 유사도: {result.get('confidence', 0):.3f}")
            print(f"검색 결과 수: {len(result.get('contexts', []))}")

            for i, ctx in enumerate(result.get('contexts', [])):
                print(f"\n[{i+1}] {ctx['category']} (유사도: {ctx['similarity']:.3f})")
                print(f"타입: {ctx['type']}")
                print(f"내용: {ctx['content'][:100]}...")
                print(f"출처: {ctx['source']}")

        except Exception as e:
            print(f"❌ 검색 테스트 실패: {e}")

    async def clear_vector_db(self, agent_type: str):
        """특정 에이전트의 벡터 DB를 초기화합니다."""
        print(f"⚠️ {agent_type} 벡터 DB를 초기화합니다. 모든 데이터가 삭제됩니다.")
        confirm = input("계속하시겠습니까? (y/N): ")

        if confirm.lower() == 'y':
            try:
                store = VectorStoreFactory.get_store(agent_type)
                success = store.clear_collection()

                if success:
                    print(f"✅ {agent_type} 벡터 DB 초기화 완료")
                else:
                    print(f"❌ {agent_type} 벡터 DB 초기화 실패")

            except Exception as e:
                print(f"❌ 초기화 중 오류: {e}")
        else:
            print("취소됨")

    async def add_single_knowledge(self, agent_type: str, content: str,
                                 knowledge_type: str, category: str,
                                 confidence: float = 0.8):
        """단일 지식을 추가합니다."""
        try:
            manager = await KnowledgeManagerFactory.get_manager(agent_type)

            success = await manager.add_new_knowledge(
                content=content,
                knowledge_type=knowledge_type,
                category=category,
                confidence=confidence,
                source="manual_input"
            )

            if success:
                print(f"✅ {agent_type}에 새 지식 추가 완료")
            else:
                print(f"❌ {agent_type} 지식 추가 실패")

        except Exception as e:
            print(f"❌ 지식 추가 중 오류: {e}")


async def main():
    manager = RAGDataManager()

    if len(sys.argv) < 2:
        print("사용법: python scripts/manage_rag_data.py [command] [options]")
        print("\n명령어:")
        print("  status                    - 전체 RAG 시스템 상태 표시")
        print("  refresh [agent_type]      - 지식 베이스 새로고침")
        print("  test agent_type query     - 검색 기능 테스트")
        print("  clear agent_type          - 벡터 DB 초기화")
        print("  add agent_type content    - 단일 지식 추가")
        print("\n에이전트 타입: source_code, binary, log_conf")
        return

    command = sys.argv[1]

    if command == "status":
        await manager.show_status()

    elif command == "refresh":
        agent_type = sys.argv[2] if len(sys.argv) > 2 else None
        await manager.refresh_knowledge_base(agent_type)

    elif command == "test":
        if len(sys.argv) < 4:
            print("사용법: python scripts/manage_rag_data.py test agent_type query")
            return
        agent_type = sys.argv[2]
        query = " ".join(sys.argv[3:])
        await manager.test_search(agent_type, query)

    elif command == "clear":
        if len(sys.argv) < 3:
            print("사용법: python scripts/manage_rag_data.py clear agent_type")
            return
        agent_type = sys.argv[2]
        await manager.clear_vector_db(agent_type)

    elif command == "add":
        if len(sys.argv) < 4:
            print("사용법: python scripts/manage_rag_data.py add agent_type content")
            return
        agent_type = sys.argv[2]
        content = " ".join(sys.argv[3:])
        await manager.add_single_knowledge(
            agent_type=agent_type,
            content=content,
            knowledge_type="manual",
            category="user_input"
        )

    else:
        print(f"알 수 없는 명령어: {command}")


if __name__ == "__main__":
    asyncio.run(main())