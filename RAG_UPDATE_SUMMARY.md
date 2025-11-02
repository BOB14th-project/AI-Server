# RAG 지식베이스 업데이트 요약

한국 암호 참조 문서(korean_crypto_rag_reference.json)를 포함하여 RAG 지식베이스를 재구축했습니다.

## 업데이트 내용

### 1. 새로운 지식 추가

**korean_crypto_rag_reference.json** 파일이 common 폴더에 추가되었습니다. 이 파일은 다음을 포함합니다:

#### 블록 암호 (Block Ciphers)
- **SEED**: 한국 은행 표준 암호 (Feistel, 16 rounds, 128-bit)
- **ARIA**: 한국 정부 표준 암호 (Involution SPN, 12/14/16 rounds)
- **HIGHT**: 경량 IoT 암호 (64-bit blocks, 32 rounds)
- **LEA**: 고속 소프트웨어 암호 (ARX 구조, 24/28/32 rounds)

#### 해시 함수 (Hash Functions)
- **HAS-160**: 한국 표준 해시 (160-bit 출력, 80 rounds)
- **LSH**: 현대 한국 해시 (224/256/384/512-bit 출력)

#### 서명 알고리즘 (Signature Algorithms)
- **KCDSA**: 한국 디지털 서명 표준
- **EC-KCDSA**: 타원곡선 기반 KCDSA

### 2. 파싱 로직 개선

`knowledge_manager.py`의 `_parse_json_data()` 함수에 한국 암호 참조 문서를 위한 전용 파싱 로직을 추가했습니다:

- **Technical characteristics** 파싱
- **Code indicators** 추출
- **Structural fingerprints** 처리
- **Detection patterns** 생성

### 3. Common 폴더 지원

모든 에이전트가 common 폴더의 JSON 파일을 공유합니다:

- `data/rag_knowledge_base/common/` 폴더의 모든 JSON 파일
- `manage_rag_data.py`가 common 폴더를 자동으로 로드
- `knowledge_manager.py`가 common 디렉토리를 통합 처리

## 재구축 결과

### Source Code Agent
- **문서 수**: 51개 → **73개** (+22개)
- Common 폴더: 57개 항목 (korean_crypto_rag_reference: 22개 포함)
- 에이전트별 폴더: 16개 항목

### Assembly Binary Agent
- **문서 수**: 54개 → **76개** (+22개)
- Common 폴더: 57개 항목 (korean_crypto_rag_reference: 22개 포함)
- 에이전트별 폴더: 19개 항목

### Logs Config Agent
- **문서 수**: 139개 → **161개** (+22개)
- Common 폴더: 57개 항목 (korean_crypto_rag_reference: 22개 포함)
- 에이전트별 폴더: 104개 항목

## 검색 성능 테스트

### SEED 알고리즘 검색
```bash
쿼리: "SEED algorithm Korean banking cipher Feistel"
결과:
1. SEED_Block_Cipher_Structure (유사도: 0.502)
2. SEED detection indicators (유사도: 0.484)
3. SEED technical characteristics (유사도: 0.474)
```

### ARIA 알고리즘 검색
```bash
쿼리: "ARIA involution SPN Korean government encryption"
결과:
1. ARIA code indicators (유사도: 0.506)
2. ARIA technical characteristics (유사도: 0.457)
3. SEED usage context (유사도: 0.062)
```

### LSH 해시 함수 검색
```bash
쿼리: "LSH hash Korean modern blockchain"
결과:
1. LSH usage patterns (유사도: 0.442)
2. LSH configuration (유사도: 0.426)
3. LSH detection indicators (유사도: 0.389)
```

## 주요 개선사항

### 1. 한국 암호 탐지 능력 향상

- 한국 표준 암호 알고리즘 (SEED, ARIA, HIGHT, LEA) 탐지
- 한국 해시 함수 (HAS-160, LSH) 인식
- 한국 서명 알고리즘 (KCDSA, EC-KCDSA) 식별

### 2. 코드 인디케이터 강화

각 알고리즘마다 다음 정보 제공:
- 클래스 이름 패턴
- 함수 이름 패턴
- 변수 이름 패턴
- 구조적 특징 (Fingerprints)

### 3. 컨텍스트 기반 탐지

알고리즘 사용 컨텍스트 정보:
- SEED: 은행, 금융 시스템
- ARIA: 정부 통신, 공식 문서
- HIGHT: IoT 기기, RFID
- LEA: 모바일 결제, 고속 암호화
- LSH: 블록체인, 현대 정부 시스템

## 사용 방법

### 지식베이스 상태 확인
```bash
python scripts/manage_rag_data.py status
```

### 지식베이스 새로고침 (재임베딩)
```bash
python scripts/manage_rag_data.py refresh
```

### 특정 에이전트만 새로고침
```bash
python scripts/manage_rag_data.py refresh source_code
python scripts/manage_rag_data.py refresh assembly_binary
python scripts/manage_rag_data.py refresh logs_config
```

### 검색 테스트
```bash
python scripts/manage_rag_data.py test source_code "SEED Korean cipher"
python scripts/manage_rag_data.py test assembly_binary "ARIA encryption"
python scripts/manage_rag_data.py test logs_config "LSH hash function"
```

## 기대 효과

1. **한국 암호 알고리즘 탐지율 향상**: SEED, ARIA, LEA, HIGHT 등 한국 표준 암호를 정확히 식별
2. **난독화된 구현 탐지**: 알고리즘 이름이 명시되지 않아도 구조적 특징으로 탐지 가능
3. **컨텍스트 기반 분석**: 사용 환경(은행, 정부, IoT)에 따른 맥락 있는 분석
4. **거짓 양성 감소**: 다중 인디케이터 매칭으로 정확도 향상

## 파일 구조

```
data/rag_knowledge_base/
├── common/                          # 모든 에이전트가 공유
│   ├── SEED_Algorithm.json
│   ├── ARIA_Algorithm.json (HIGHT, LEA, LSH)
│   └── korean_crypto_rag_reference.json  ⭐ 새로 추가
├── source_code/
│   └── structural_crypto_patterns.json
├── assembly_binary/
│   └── x86_x64_crypto_assembly.json
└── logs_config/
    ├── tls_cipher_suites.json
    └── ssh_security_patterns.json
```

## 다음 단계

1. **실제 파일 테스트**: 한국 암호가 포함된 실제 소스코드/바이너리로 테스트
2. **임계값 조정**: 탐지 신뢰도 임계값 최적화
3. **추가 알고리즘**: 필요시 다른 국가 표준 암호 추가
4. **성능 모니터링**: 검색 응답 시간 및 정확도 측정
