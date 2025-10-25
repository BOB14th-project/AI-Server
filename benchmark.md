# AI Benchmark for Quantum-Vulnerable Cryptography Detection

양자 취약 암호 알고리즘 탐지를 위한 AI 모델 성능 평가 벤치마크 시스템

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)]()

## 🎯 프로젝트 개요

포스트 양자 암호(Post-Quantum Cryptography) 전환을 대비하여 기존 시스템의 양자 취약 암호 알고리즘을 탐지하는 AI 모델들의 성능을 종합적으로 평가하는 벤치마크 시스템입니다.

### 주요 특징

- **다중 AI 모델 지원**: 상용 API 3개 + 로컬 Ollama 모델 3개
- **4가지 분석 도메인**: 소스코드, 어셈블리/바이너리, 동적분석, 로그/설정
- **한국 국산 암호**: SEED, ARIA, HIGHT, LEA, KCDSA 등 특화 탐지
- **종합 성능 분석**: 정확도, 속도, 토큰 효율성 등 다각도 평가
- **183개 테스트 케이스**: 실제 환경을 반영한 다양한 시나리오

## 📚 상세 문서

- **[평가 메트릭 및 점수 계산](docs/METRICS.md)** - F1 Score, Precision, Recall 등 상세 계산 방법
- **[테스트 파일 생성 가이드](docs/TEST_FILES.md)** - 테스트 케이스 생성 방법 및 현황
- **[프로젝트 상세 문서](CLAUDE.md)** - 전체 아키텍처 및 사용 가이드

## 🧪 지원 모델

### 상용 API 모델
| 프로바이더 | 모델 | 특징 |
|-----------|------|------|
| **Google** | `gemini-2.0-flash-exp` | 높은 정확도, 상세한 분석 |
| **OpenAI** | `gpt-4.1` | 균형잡힌 성능 |
| **xAI** | `grok-3-mini` | 빠른 응답, 경량화 |

### 로컬 Ollama 모델
| 모델 | 크기 | 특징 |
|------|------|------|
| **LLaMA 3** | `llama3:8b` | 범용 성능, 로컬 실행 |
| **Qwen 3** | `qwen3:8b` | 멀티모달 특화 |
| **Code Llama** | `codellama:7b` | 코드 분석 최적화 |

## 📊 분석 에이전트 및 테스트 데이터

### 🔍 Source Code Agent (80개 테스트 파일)
- **대상**: Python, Java, C/C++, JavaScript, TypeScript 소스 코드
- **탐지**: RSA, ECC, DH, DSA, 한국 암호 알고리즘
- **특화**: 코드 패턴 분석, 라이브러리 사용 탐지
- **예시**: RSA 키 생성, ECDSA 서명, SEED 암호화 구현

### ⚙️ Assembly Binary Agent (80개 테스트 파일)
- **대상**: 어셈블리 코드, 바이너리 덤프, 디스어셈블리
- **탐지**: 모듈러 지수 연산, 타원곡선 연산, 큰 정수 연산
- **특화**: 컴파일된 코드의 암호 연산 시그니처 분석
- **예시**: RSA 모듈러 연산, ECC 스칼라 곱셈, ChaCha20 구현

### 📈 Dynamic Analysis Agent (6개 테스트 파일)
- **대상**: 런타임 데이터, API 호출 로그, 메모리 덤프
- **탐지**: 암호화 API 사용 패턴, 메모리 할당, 성능 특성
- **특화**: 실행 시 행동 분석, 간접적 암호 사용 증거
- **예시**: OpenSSL API 호출, 암호 연산 타이밍, 메모리 패턴

### 📋 Logs Config Agent (17개 테스트 파일)
- **대상**: 설정 파일, 시스템 로그, 애플리케이션 로그
- **탐지**: SSL/TLS 설정, 인증서 구성, 암호 라이브러리 설정
- **특화**: 설정 기반 암호 사용, 로그의 암호 이벤트
- **예시**: Apache SSL 설정, VPN 설정, HSM 로그, 한국 암호 라이브러리 설정

**총 183개 테스트 파일** - 각 파일에 대응하는 ground_truth JSON 포함

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/AI--Benchmark.git
cd AI--Benchmark

# 의존성 설치
pip install -r requirements.txt

# Ollama 설치 (macOS)
brew install ollama

# Ollama 모델 다운로드
ollama pull llama3:8b
ollama pull qwen3:8b
ollama pull codellama:7b

# Ollama 서버 실행
ollama serve
```

### 2. API 키 설정

`config/config.yaml` 파일에 API 키를 설정하세요:

```yaml
llm_providers:
  google:
    api_key: "your_google_api_key_here"
    model: "gemini-2.0-flash-exp"

  openai:
    api_key: "your_openai_api_key_here"
    model: "gpt-4.1"

  xai:
    api_key: "your_xai_api_key_here"
    model: "grok-3-mini"
```

### 3. 시스템 테스트

```bash
# 전체 시스템 테스트
python test_benchmark_system.py

# 예상 출력:
# 🧪 AI 벤치마크 시스템 테스트
# ============================================================
# 🔧 설정 로더 테스트...
#   ✅ google 설정 완료
#   ✅ 설정 로더 정상 작동
# 🤖 Ollama 연결 테스트...
#   ✅ Ollama 서버 연결됨
#   📋 사용 가능한 모델: ['llama3:8b', 'codellama:7b', 'qwen3:8b']
```

## 📋 사용법

### 전체 벤치마크 실행

```bash
# 모든 모델로 소규모 테스트 (에이전트당 3개 파일)
python benchmark_runner.py --limit 3

# 특정 프로바이더만 테스트
python benchmark_runner.py --providers google ollama --limit 5

# 특정 에이전트만 테스트
python benchmark_runner.py --agents source_code assembly_binary --limit 2

# 병렬 실행 (빠른 처리)
python benchmark_runner.py --parallel --limit 3

# 전체 벤치마크 (모든 파일)

python benchmark_runner.py
```

### 결과 분석 (통합 도구)

```bash
# 전체 분석 및 시각화 (권장)
python analyze_and_visualize.py benchmark_results.json

# 출력 디렉토리 지정
python analyze_and_visualize.py benchmark_results.json --output-dir my_results

# 최소 테스트 수 설정 (통계적 신뢰도)
python analyze_and_visualize.py benchmark_results.json --min-tests 20

# 텍스트 리포트만
python analyze_and_visualize.py benchmark_results.json --text-only

# 시각화만
python analyze_and_visualize.py benchmark_results.json --visualize-only
```

**생성되는 결과물:**
- 📄 `COMPREHENSIVE_REPORT.txt` - 종합 텍스트 보고서
- 📊 `model_f1_comparison.png` - 모델별 F1 Score 비교
- 📊 `precision_recall_f1.png` - Precision/Recall/F1 비교
- 📊 `agent_performance.png` - 에이전트별 성능
- 📊 `model_response_time.png` - 모델별 응답시간
- 📊 `algorithm_detection_overall.png` - 알고리즘 탐지율
- 📊 `model_agent_heatmap.png` - 모델-에이전트 히트맵

### 단일 파일 테스트

```bash
# 특정 파일로 빠른 테스트
python test_single_file.py
```

## 📈 성능 지표

### 핵심 평가 메트릭 (상세 내용은 [METRICS.md](docs/METRICS.md) 참조)

- **탐지 정확도 (Detection Accuracy)**: 양자 취약 알고리즘 탐지율
- **정밀도 (Precision)**: TP / (TP + FP) - 거짓양성 최소화
- **재현율 (Recall)**: TP / (TP + FN) - 거짓음성 최소화
- **F1 점수**: 2 × (Precision × Recall) / (Precision + Recall)
- **응답 시간 (Response Time)**: API 호출부터 응답까지
- **토큰 효율성**: F1 점수 / 총 토큰 수
- **JSON 유효성**: 구조화된 출력 생성 능력

### 예상 성능 (F1 점수 기준)

| 모델 | 예상 F1 | 응답 시간 | 토큰 효율성 | 특징 |
|------|---------|-----------|-------------|------|
| gemini-2.0-flash-exp | 0.85-0.90 | 10-15초 | 높음 | 최고 정확도, 상세한 분석 |
| gpt-4.1 | 0.80-0.85 | 8-12초 | 중간 | 균형잡힌 성능 |
| grok-3-mini | 0.75-0.80 | 5-8초 | 높음 | 빠른 응답, 경량화 |
| llama3:8b | 0.70-0.75 | 3-5초 | 매우높음 | 로컬 실행, 빠름 |
| qwen3:8b | 0.65-0.70 | 4-6초 | 높음 | 멀티모달 특화 |
| codellama:7b | 0.60-0.65 | 2-4초 | 매우높음 | 코드 특화, 빠름 |

## 📁 프로젝트 구조

```
AI--Benchmark/
├── 📋 README.md                      # 이 파일
├── 📄 CLAUDE.md                      # 프로젝트 상세 문서
├── ⚙️ benchmark_runner.py            # 메인 벤치마크 실행기
├── 📊 analyze_and_visualize.py       # 통합 분석/시각화 도구 (권장)
├── 📊 analyze_*.py                   # 개별 분석 도구들 (레거시)
├── 📊 visualize_*.py                 # 개별 시각화 도구들 (레거시)
├── 🧪 test_benchmark_system.py       # 시스템 테스트
├── 📄 requirements.txt               # 의존성 목록
│
├── 📁 docs/                          # 추가 문서들
│   ├── METRICS.md                   # 평가 메트릭 상세 설명
│   └── TEST_FILES.md                # 테스트 파일 생성 가이드
│
├── 🔧 config/                        # 설정 파일들
│   ├── config.yaml                  # 메인 설정 파일
│   └── config_loader.py             # 설정 로더
│
├── 🤖 agents/                        # 분석 에이전트들
│   ├── base_agent.py                # 기본 에이전트
│   ├── source_code_agent.py         # 소스코드 분석 (80개 파일)
│   ├── assembly_agent.py            # 어셈블리 분석 (80개 파일)
│   ├── dynamic_analysis_agent.py    # 동적 분석 (6개 파일)
│   ├── logs_config_agent.py         # 로그/설정 분석 (17개 파일)
│   └── agent_factory.py             # 에이전트 팩토리
│
├── 🌐 clients/                       # LLM API 클라이언트들
│   ├── base_client.py               # 기본 클라이언트
│   ├── google_client.py             # Google Gemini
│   ├── openai_client.py             # OpenAI GPT
│   ├── xai_client.py                # xAI Grok
│   ├── ollama_client.py             # Ollama 로컬
│   └── client_factory.py            # 클라이언트 팩토리
│
├── 📂 data/                          # 테스트 데이터 (183개 파일)
│   ├── test_files/                  # 실제 테스트 파일들
│   │   ├── source_code/             # 소스코드 샘플 (80개)
│   │   ├── assembly_binary/         # 어셈블리 샘플 (80개)
│   │   ├── dynamic_analysis/        # 동적분석 데이터 (6개)
│   │   └── logs_config/             # 로그/설정 (17개)
│   └── ground_truth/                # 정답 데이터 (183개 JSON)
│
├── 🛠️ utils/                         # 유틸리티
│   ├── test_case_manager.py         # 테스트 케이스 관리
│   └── metrics_calculator.py        # 성능 메트릭 계산
│
├── 📜 scripts/                       # 추가 스크립트들
│   ├── test_single_file.py          # 단일 파일 테스트
│   ├── test_available_models.py     # 모델 가용성 확인
│   └── (기타 개발/테스트 스크립트)
│
├── 📊 results/                       # 결과 파일들 (JSON + CSV)
└── 📋 reports/                       # 분석 리포트들
```

## 🔍 탐지 대상 암호 알고리즘

### Shor 알고리즘에 취약한 공개키 암호
- **RSA**: 모든 키 크기 (1024, 2048, 3072, 4096비트)
- **ECC**: secp256r1, secp384r1, secp521r1, Curve25519, Ed25519, secp256k1
- **DH/DSA**: Diffie-Hellman, DSA, ElGamal (모든 키 크기)
- **BLS**: BLS12-381 페어링 기반 암호

### 한국 국산 암호 알고리즘
- **대칭키**: SEED, ARIA, HIGHT, LEA
- **공개키**: KCDSA, EC-KCDSA (양자 취약)
- **해시**: HAS-160, LSH (Grover 취약)

### Grover 알고리즘에 취약한 대칭키/해시
- **블록암호**: AES-128 (→64비트 보안강도), 3DES, DES, RC4, RC2
- **해시함수**: MD5, SHA-1, SHA-256, BLAKE2b, SipHash

### 양자 내성 알고리즘 (탐지 대상 아님)
- **격자 기반**: Kyber, Dilithium, NTRU
- **해시 기반**: SPHINCS+
- **대칭키**: AES-256 (128비트 양자 보안강도 유지)

## 📊 예제 결과

```bash
$ python benchmark_runner.py --limit 2

🚀 벤치마크 시작
============================================================
✅ Ollama 사용 가능한 모델: ['llama3:8b', 'codellama:7b']
📁 source_code: 2개 테스트 파일 로드됨
📁 assembly_binary: 2개 테스트 파일 로드됨
📁 dynamic_analysis: 2개 테스트 파일 로드됨
📁 logs_config: 2개 테스트 파일 로드됨
📊 총 24개 테스트 조합 (3개 프로바이더 × 4개 에이전트 × 2개 파일)

📋 테스트 1/24: google/gemini-2.0-flash-exp/source_code
    파일: rsa_public_key_system.java
    ✅ 완료 (13.2초)
    🎯 정확도: 0.850
    📊 F1 Score: 0.878
    🔍 탐지: RSA, SHA-256, PKCS

📋 테스트 2/24: ollama/llama3:8b/source_code
    파일: rsa_public_key_system.java
    ✅ 완료 (4.1초)
    🎯 정확도: 0.720
    📊 F1 Score: 0.745
    🔍 탐지: RSA, SHA-256

============================================================