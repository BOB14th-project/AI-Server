#!/usr/bin/env python3
"""RAG 개선사항 테스트 스크립트"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def test_similarity_threshold():
    """유사도 임계값 테스트"""

    print("=" * 80)
    print("🧪 RAG 유사도 임계값 테스트")
    print("=" * 80)

    test_cases = {
        "source_code": {
            "query": "import rsa\nkey = rsa.newkeys(2048)",
            "threshold": 0.10
        },
        "assembly_binary": {
            "query": "RSA_public_encrypt\nRSA_private_decrypt",
            "threshold": 0.05
        }
    }

    for agent_type, config in test_cases.items():
        print(f"\n{'='*80}")
        print(f"📝 Testing {agent_type.upper()} agent")
        print(f"   임계값: {config['threshold']}")
        print(f"{'='*80}")

        km = await KnowledgeManagerFactory.get_manager(agent_type)

        # 원본 검색 (필터링 전)
        result = await km.search_relevant_context(config['query'], top_k=5)
        contexts = result.get("contexts", [])

        print(f"\n📊 검색 결과 (총 {len(contexts)}개):")
        for i, ctx in enumerate(contexts, 1):
            similarity = ctx['similarity']
            status = "✅ 통과" if similarity >= config['threshold'] else "❌ 필터링됨"
            print(f"   {i}. {ctx['category']:30} | 유사도: {similarity:6.3f} | {status}")

        # 필터링 후 개수
        filtered = [c for c in contexts if c['similarity'] >= config['threshold']]
        print(f"\n✅ 필터링 후: {len(filtered)}개 (임계값 {config['threshold']} 이상)")
        print(f"❌ 제외됨: {len(contexts) - len(filtered)}개")

async def test_binary_scan_range():
    """Binary 에이전트 스캔 범위 테스트"""

    print("\n" + "=" * 80)
    print("🧪 Binary 에이전트 스캔 범위 테스트")
    print("=" * 80)

    # 간단한 더미 바이너리 생성 (50KB)
    dummy_binary = b"RSA_public_encrypt\x00" * 100
    dummy_binary += b"ECDSA_sign\x00" * 100
    dummy_binary += b"CryptGenKey\x00" * 100
    dummy_binary += b"\x00\xff" * 20000  # 바이너리 데이터로 채우기

    print(f"\n📊 테스트 바이너리 크기: {len(dummy_binary):,} 바이트")

    from pqc_inspector_server.agents.assembly_binary import AssemblyBinaryAgent

    agent = AssemblyBinaryAgent()
    extracted_strings = agent._extract_strings_from_binary(dummy_binary)

    lines = extracted_strings.split('\n')
    print(f"✅ 추출된 문자열 수: {len(lines)}개")
    print(f"\n📄 추출된 문자열 샘플 (처음 10개):")
    for i, line in enumerate(lines[:10], 1):
        print(f"   {i}. {line}")

async def main():
    """메인 테스트 함수"""
    print("\n" + "🚀 " * 20)
    print("RAG 개선사항 테스트 시작")
    print("🚀 " * 20 + "\n")

    # 1. 유사도 임계값 테스트
    await test_similarity_threshold()

    # 2. Binary 스캔 범위 테스트
    await test_binary_scan_range()

    print("\n" + "✅ " * 20)
    print("모든 테스트 완료!")
    print("✅ " * 20 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
