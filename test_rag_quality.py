#!/usr/bin/env python3
"""RAG 검색 품질 테스트"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def test_rag_searches():
    """각 에이전트별로 대표적인 쿼리를 테스트"""

    test_cases = {
        "source_code": [
            "import rsa\nkey = rsa.newkeys(2048)",
            "from cryptography.hazmat.primitives.asymmetric import rsa",
            "RSA.generate(2048)"
        ],
        "logs_config": [
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "Certificate signature algorithm: sha256WithRSAEncryption",
            "Server host key: ssh-rsa"
        ],
        "assembly_binary": [
            "RSA_public_encrypt\nRSA_private_decrypt",
            "CryptGenKey\nCryptSignHash",
            "ECDSA_sign\nECDSA_verify"
        ]
    }

    for agent_type, queries in test_cases.items():
        print(f"\n{'='*80}")
        print(f"🧪 Testing {agent_type.upper()} agent")
        print(f"{'='*80}")

        # KnowledgeManagerFactory를 사용하여 초기화
        km = await KnowledgeManagerFactory.get_manager(agent_type)

        for i, query in enumerate(queries, 1):
            print(f"\n📝 Query {i}: {query[:80]}...")
            result = await km.search_relevant_context(query, top_k=3)

            contexts = result.get("contexts", [])
            print(f"   Found {len(contexts)} results")

            for j, ctx in enumerate(contexts, 1):
                print(f"\n   Result {j}:")
                print(f"     Category: {ctx['category']}")
                print(f"     Type: {ctx['type']}")
                print(f"     Similarity: {ctx['similarity']:.3f}")
                print(f"     Content: {ctx['content'][:150]}...")

            if len(contexts) == 0:
                print("   ⚠️ No results found!")

if __name__ == "__main__":
    asyncio.run(test_rag_searches())
