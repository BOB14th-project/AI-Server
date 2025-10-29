# Assembly/Binary RAG 최적화 보고서

## 🎯 문제점

### 벤치마크 결과
```
assembly_binary: RAG F1=0.400 (TP=8, FP=8, FN=16), 순수 F1=0.550 (TP=11, FP=5, FN=13)
RAG 효과: -27.3% (성능 저하)
```

### 문제 분석
- **TP 감소**: 11 → 8 (3개 놓침)
- **FP 증가**: 5 → 8 (3개 오탐)
- **FN 증가**: 13 → 16 (3개 더 놓침)

RAG 컨텍스트가 LLM의 직접 분석을 방해하고 있었음.

---

## 🔍 근본 원인 분석

### 1. RAG 컨텍스트 품질 테스트 결과

`scripts/optimize_binary_rag.py`를 실행한 결과:

**좋은 소식**: RAG 자체는 잘 작동함
- 암호화 관련 쿼리: 유사도 0.20~0.27 (높음)
- 일반 코드 쿼리: 유사도 < 0.05 (자동 필터링)
- **모든 설정에서 False Positive = 0**

### 2. 진짜 문제

RAG가 아닌 **프롬프트와 사용 방식**이 문제:

#### 문제 1: 권위적 프롬프트
```python
# 이전 (나쁜 예)
"위의 전문가 지식을 바탕으로 다음 바이너리를 분석하세요"
```
→ LLM이 RAG에 과도하게 의존, 직접 분석 소홀

#### 문제 2: 낮은 임계값
- 임계값 0.05: 관련성 낮은 컨텍스트도 포함
- 유사도 0.05~0.15 범위의 "애매한" 패턴이 혼란 유발

#### 문제 3: 과도한 컨텍스트
- top_k=5: 너무 많은 패턴 제공
- 3000자: 긴 컨텍스트가 중요 정보 희석

---

## ✅ 적용된 개선사항

### 1. 임계값 상향 조정
**파일**: `pqc_inspector_server/agents/base_agent.py`

```python
# Before
"assembly_binary": 0.05,  # 너무 낮음

# After
"assembly_binary": 0.15,  # 3배 상향 (품질 향상)
```

**효과**:
- 유사도 < 0.15 패턴 자동 필터링
- 관련성 높은 패턴만 사용
- False Positive 감소 예상

---

### 2. 프롬프트 개선
**파일**: `pqc_inspector_server/agents/assembly_binary.py`

#### Before (권위적, 의존 유도)
```python
prompt = f"""다음 바이너리 파일을 분석하여 비양자내성암호 사용 여부를 확인해주세요.

{rag_context}

위의 전문가 지식을 바탕으로 다음 바이너리를 분석하세요:
"""
```

#### After (참고용, 독립적 분석)
```python
# 조건부 RAG: 의미있을 때만 포함
if rag_context and "관련 지식이 없습니다" not in rag_context:
    context_hint = f"""
[참고용 암호화 패턴 힌트]
다음은 일반적인 암호화 패턴의 예시입니다. 이는 참고만 하고, 실제 바이너리 내용을 직접 분석하여 판단하세요:

{rag_context}
---
"""

prompt = f"""다음 바이너리 파일을 분석하여 비양자내성암호 사용 여부를 확인해주세요.

{context_hint}
[분석 대상 바이너리]
...

중요: 위의 힌트는 참고만 하고, 실제 바이너리 문자열을 직접 분석하여 암호화 알고리즘 사용 여부를 판단하세요.
발견된 문자열이 실제로 암호화 알고리즘과 관련이 있는지 신중히 평가하세요.
"""
```

**핵심 변경점**:
1. **"전문가 지식을 바탕으로"** → **"참고만 하고"**
2. **조건부 포함**: 관련 없으면 컨텍스트 생략
3. **직접 분석 강조**: "실제 바이너리 내용을 직접 분석"
4. **신중한 평가 요구**: "신중히 평가하세요"

---

### 3. top_k 감소
```python
# Before
rag_context = await self._get_rag_context(content_text[:3000], top_k=5)

# After
rag_context = await self._get_rag_context(content_text[:1500], top_k=2)
```

**변경점**:
- **top_k**: 5 → 2 (60% 감소)
- **쿼리 길이**: 3000자 → 1500자 (50% 감소)

**효과**:
- 가장 관련성 높은 2개 패턴만 사용
- 노이즈 감소
- 컨텍스트 간결화

---

## 📊 예상 개선 효과

### 시나리오별 분석

#### 시나리오 1: 명확한 암호화 사용 (RSA_public_encrypt)
- **유사도**: 0.24 (높음)
- **Before**: RAG 제공 → LLM이 RAG에 의존
- **After**: RAG 제공 + "참고만" 명시 → LLM이 직접 분석도 병행
- **예상**: TP 유지, 더 정확한 판단

#### 시나리오 2: 애매한 패턴 (mod_exp, mul 등)
- **유사도**: 0.10 (낮음)
- **Before**: RAG 제공 (임계값 0.05) → 혼란 유발 → FP 증가
- **After**: RAG 필터링 (임계값 0.15) → 순수 LLM 분석
- **예상**: FP 감소

#### 시나리오 3: 일반 코드 (strlen, memcpy)
- **유사도**: 0.03 (매우 낮음)
- **Before**: RAG 필터링 → 순수 LLM
- **After**: RAG 필터링 → 순수 LLM
- **예상**: 변화 없음

---

## 🎯 예상 성능 지표

### Conservative (보수적 예측)
```
Before: F1=0.400 (TP=8, FP=8, FN=16)
After:  F1=0.500 (TP=10, FP=6, FN=14)
개선:   +25%
```

### Optimistic (낙관적 예측)
```
Before: F1=0.400 (TP=8, FP=8, FN=16)
After:  F1=0.550 (TP=11, FP=5, FN=13)
개선:   +37.5% (순수 LLM 수준 회복)
```

### 개선 근거
1. **FP 감소**: 임계값 상향으로 애매한 패턴 필터링 (8 → 5-6)
2. **TP 회복**: 프롬프트 개선으로 직접 분석 강화 (8 → 10-11)
3. **FN 감소**: RAG 의존도 감소로 놓침 감소 (16 → 13-14)

---

## 🧪 검증 방법

### 테스트 스크립트
```bash
# RAG 품질 분석
python scripts/optimize_binary_rag.py

# 최종 개선사항 테스트
python scripts/test_final_improvements.py
```

### 벤치마크 재실행
```bash
# 전체 벤치마크 (실제 성능 측정)
python scripts/run_benchmark.py
```

---

## 📋 개선사항 요약

| 항목 | Before | After | 개선 효과 |
|------|--------|-------|-----------|
| **임계값** | 0.05 | 0.15 | 품질 향상 (3배) |
| **top_k** | 5 | 2 | 노이즈 감소 (60%) |
| **쿼리 길이** | 3000자 | 1500자 | 효율성 (50%) |
| **프롬프트** | "전문가 지식 바탕" | "참고만" | 독립성 강화 |
| **조건부 RAG** | 항상 제공 | 의미있을 때만 | 선택적 활용 |

---

## 💡 추가 개선 아이디어 (선택사항)

### 1. Assembly 전용 패턴만 사용
**현재**: Common 디렉토리 패턴 포함 (RSA, ECDSA 상세 구조)
**문제**: 상세 구조가 바이너리 분석에 오히려 혼란
**대안**: Assembly 전용 패턴만 로드

```python
# knowledge_manager.py 수정
if agent_type == "assembly_binary":
    # Common 디렉토리 제외
    skip_common = True
```

### 2. 하이브리드 모드
유사도에 따라 RAG 사용 방식 변경:
- **High (>0.20)**: RAG 적극 활용
- **Medium (0.15-0.20)**: RAG 참고용
- **Low (<0.15)**: RAG 무시, 순수 LLM

### 3. 네거티브 샘플 추가
지식 베이스에 "이것은 암호화가 아님" 패턴 추가:
- `strlen`, `memcpy`: 일반 함수
- `add`, `mul`: 일반 연산
→ FP 추가 감소

---

## 🚀 다음 단계

1. ✅ **코드 수정 완료**
   - base_agent.py: 임계값 0.05 → 0.15
   - assembly_binary.py: 프롬프트 개선, top_k 2

2. ⏳ **벤치마크 재실행** (사용자 실행 필요)
   ```bash
   python scripts/run_benchmark.py
   ```

3. ⏳ **결과 분석**
   - F1 Score 개선 확인
   - TP, FP, FN 변화 측정
   - -27.3% → 0% 이상 목표

4. ⏳ **추가 조정**
   - 결과에 따라 임계값 미세 조정
   - 필요시 Assembly 전용 모드 구현

---

## 📝 작성 일시
현재 세션

## ✍️ 작성자
Claude Code

## 📊 관련 문서
- `docs/RAG_IMPROVEMENT_REPORT.md`: 전체 RAG 개선 보고서
- `docs/LOGS_CONFIG_EXPANSION_COMPLETE.md`: Logs/Config 확장 보고서
- `scripts/optimize_binary_rag.py`: RAG 품질 분석 스크립트
