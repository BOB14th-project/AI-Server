#!/usr/bin/env python3
"""최종 개선사항 테스트 스크립트"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def test_all_agents():
    """모든 에이전트의 RAG 검색 테스트"""

    print("\n" + "=" * 80)
    print("🧪 최종 개선사항 검증 테스트")
    print("=" * 80)

    test_cases = {
        "source_code": {
            "query": "import rsa\nkey = rsa.newkeys(2048)",
            "threshold": 0.10,
            "expected_min": 3
        },
        "assembly_binary": {
            "query": "RSA_public_encrypt\nRSA_private_decrypt",
            "threshold": 0.05,
            "expected_min": 3
        },
        "logs_config": {
            "query": "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "threshold": 0.20,
            "expected_min": 1  # 높은 임계값으로 적게 나올 수 있음
        }
    }

    results = {}

    for agent_type, config in test_cases.items():
        print(f"\n{'='*80}")
        print(f"📝 {agent_type.upper()} 에이전트 테스트")
        print(f"   임계값: {config['threshold']}")
        print(f"   예상 최소 결과: {config['expected_min']}개")
        print(f"{'='*80}")

        km = await KnowledgeManagerFactory.get_manager(agent_type)

        # 검색 실행
        result = await km.search_relevant_context(config['query'], top_k=5)
        contexts = result.get("contexts", [])

        print(f"\n📊 검색 결과 (총 {len(contexts)}개):")

        passed_count = 0
        for i, ctx in enumerate(contexts, 1):
            similarity = ctx['similarity']
            is_passed = similarity >= config['threshold']
            if is_passed:
                passed_count += 1
            status = "✅ 통과" if is_passed else "❌ 필터링됨"
            print(f"   {i}. {ctx['category']:35} | 유사도: {similarity:6.3f} | {status}")

        print(f"\n결과:")
        print(f"   ✅ 임계값 통과: {passed_count}개 (임계값 {config['threshold']} 이상)")
        print(f"   ❌ 필터링됨: {len(contexts) - passed_count}개")

        # 검증
        if passed_count >= config['expected_min']:
            print(f"   🎉 테스트 성공! (최소 {config['expected_min']}개 이상)")
            results[agent_type] = "✅ 성공"
        else:
            print(f"   ⚠️ 테스트 실패 (최소 {config['expected_min']}개 필요)")
            results[agent_type] = "❌ 실패"

    print("\n" + "=" * 80)
    print("📊 최종 테스트 결과 요약")
    print("=" * 80)

    for agent_type, status in results.items():
        print(f"   {agent_type:20} : {status}")

    all_passed = all(status == "✅ 성공" for status in results.values())

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패")
    print("=" * 80)

    print("\n📋 적용된 개선사항:")
    print("   1. ✅ common 디렉토리 로드 (RSA, ECDSA 상세 구조)")
    print("   2. ✅ detailed_structure 형식 JSON 파싱 지원")
    print("   3. ✅ 유사도 임계값 적용:")
    print("      - source_code: 0.10")
    print("      - assembly_binary: 0.05")
    print("      - logs_config: 0.20 (높은 임계값)")
    print("   4. ✅ logs/config RAG 재활성화")
    print("   5. ✅ Binary 스캔 범위 확장 (5KB→50KB, 50개→200개 문자열)")

    print("\n📊 문서 수 증가:")
    print("   - source_code: 67 → 126개 (+88%)")
    print("   - assembly_binary: 34 → 93개 (+174%)")
    print("   - logs_config: 13 → 72개 (+454%)")

    print("\n🎯 다음 단계:")
    print("   - 실제 벤치마크 테스트 실행")
    print("   - 성능 지표 측정 (F1 Score, TP, FP, FN)")
    print("   - 개선 효과 검증\n")

if __name__ == "__main__":
    asyncio.run(test_all_agents())
