#!/usr/bin/env python3
"""Assembly/Binary RAG 최적화 테스트"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def test_binary_rag_quality():
    """Binary RAG 컨텍스트 품질 분석"""

    print("\n" + "="*80)
    print("🔍 Assembly/Binary RAG 품질 분석")
    print("="*80)

    # 실제 바이너리 분석 시나리오
    test_cases = [
        {
            "name": "OpenSSL RSA 함수",
            "query": "RSA_public_encrypt\nRSA_private_decrypt\nRSA_sign\nBN_mod_exp",
            "expected": "OpenSSL RSA 관련 어셈블리"
        },
        {
            "name": "ECDSA 서명 코드",
            "query": "ECDSA_sign\nEC_KEY_new\nEC_POINT_mul\nsecp256k1",
            "expected": "ECDSA 어셈블리"
        },
        {
            "name": "일반 수학 연산 (False Positive 유도)",
            "query": "add rax, rbx\nmul rcx\nmov [rsp], rax",
            "expected": "암호화 관련 없음"
        },
        {
            "name": "문자열 처리 (False Positive 유도)",
            "query": "strcmp\nstrlen\nmemcpy\nprintf",
            "expected": "암호화 관련 없음"
        }
    ]

    km = await KnowledgeManagerFactory.get_manager("assembly_binary")

    # 다양한 설정으로 테스트
    configs = [
        {"name": "현재 설정", "top_k": 5, "threshold": 0.05},
        {"name": "중간 임계값", "top_k": 3, "threshold": 0.10},
        {"name": "높은 임계값", "top_k": 3, "threshold": 0.15},
        {"name": "매우 높은 임계값", "top_k": 2, "threshold": 0.20},
    ]

    results = {}

    for config in configs:
        print(f"\n{'='*80}")
        print(f"⚙️ 설정: {config['name']} (top_k={config['top_k']}, threshold={config['threshold']})")
        print(f"{'='*80}")

        config_results = []

        for test_case in test_cases:
            print(f"\n📝 테스트: {test_case['name']}")
            print(f"   예상: {test_case['expected']}")

            result = await km.search_relevant_context(
                test_case['query'],
                top_k=config['top_k']
            )
            contexts = result.get("contexts", [])

            # 임계값 필터링
            filtered = [c for c in contexts if c['similarity'] >= config['threshold']]

            print(f"   결과: {len(contexts)}개 검색 → {len(filtered)}개 통과")

            if filtered:
                print(f"   유사도 범위: {filtered[-1]['similarity']:.3f} ~ {filtered[0]['similarity']:.3f}")
                for i, ctx in enumerate(filtered[:3], 1):
                    print(f"      {i}. {ctx['category']:30} | {ctx['similarity']:.3f}")
            else:
                print(f"   (컨텍스트 없음)")

            config_results.append({
                "test": test_case['name'],
                "total": len(contexts),
                "passed": len(filtered),
                "max_sim": filtered[0]['similarity'] if filtered else 0.0,
                "expected": test_case['expected']
            })

        results[config['name']] = config_results

    # 분석 결과
    print(f"\n{'='*80}")
    print("📊 설정별 비교 분석")
    print(f"{'='*80}")

    for config_name, config_results in results.items():
        print(f"\n{config_name}:")

        # True Positive (암호화 관련)
        tp_contexts = [r for r in config_results[:2] if r['passed'] > 0]
        # False Positive (암호화 무관)
        fp_contexts = [r for r in config_results[2:] if r['passed'] > 0]

        print(f"   ✅ 암호화 관련 탐지: {len(tp_contexts)}/2")
        print(f"   ❌ 오탐 (암호화 무관): {len(fp_contexts)}/2")

        if len(fp_contexts) == 0 and len(tp_contexts) >= 1:
            print(f"   🎯 추천 설정!")

    print(f"\n{'='*80}")
    print("💡 개선 권장사항")
    print(f"{'='*80}")

    print("""
1. 임계값 상향 조정
   - 현재 0.05는 너무 낮아 관련 없는 컨텍스트 포함
   - 권장: 0.15 이상 (False Positive 감소)

2. top_k 감소
   - 현재 5개는 너무 많아 노이즈 증가
   - 권장: 2-3개 (가장 관련성 높은 것만)

3. Common 디렉토리 선택적 사용
   - RSA/ECDSA 상세 구조가 오히려 혼란을 줄 수 있음
   - Assembly 전용 패턴만 사용 고려

4. 프롬프트 개선
   - RAG 컨텍스트를 "참고만" 하도록 명시
   - 최종 판단은 LLM이 코드 직접 분석

5. 하이브리드 접근
   - 높은 유사도(>0.15): RAG 적극 활용
   - 낮은 유사도(<0.15): RAG 무시, 순수 LLM 분석
""")

if __name__ == "__main__":
    asyncio.run(test_binary_rag_quality())
