# 📚 RAG 데이터 관리 가이드

PQC Inspector의 RAG(Retrieval-Augmented Generation) 시스템에 새로운 지식을 추가하고 관리하는 방법에 대한 포괄적인 가이드입니다.

## 🎯 개요

RAG 시스템은 각 에이전트별로 특화된 지식 베이스를 유지하여 암호화 분석의 정확도를 향상시킵니다. 새로운 암호화 패턴, 취약점 정보, 라이브러리 시그니처 등을 지속적으로 추가할 수 있습니다.

## 🏗️ RAG 시스템 구조

```
data/
├── vector_db/                    # ChromaDB 벡터 데이터베이스 (자동 생성)
│   ├── pqc_inspector_source_code/
│   ├── pqc_inspector_binary/
│   ├── pqc_inspector_parameter/
│   └── pqc_inspector_log_conf/
└── rag_knowledge_base/           # 사용자 정의 지식 베이스
    ├── source_code/              # 소스코드 관련 지식
    │   ├── patterns.json
    │   ├── libraries.json
    │   └── examples/
    ├── binary/                   # 바이너리 관련 지식
    │   ├── signatures.json
    │   ├── constants.json
    │   └── examples/
    ├── parameter/                # 설정 파일 관련 지식
    │   ├── jwt_patterns.json
    │   ├── tls_configs.json
    │   └── examples/
    └── log_conf/                 # 로그 파일 관련 지식
        ├── tls_logs.json
        ├── cert_patterns.json
        └── examples/
```

## 📝 데이터 추가 방법

### 방법 1: JSON 파일을 통한 배치 추가 (권장)

각 에이전트 디렉토리에 JSON 파일을 생성하여 새로운 지식을 추가할 수 있습니다.

#### 소스코드 패턴 추가

`data/rag_knowledge_base/source_code/new_patterns.json`:

```json
{
  "patterns": [
    {
      "type": "crypto_pattern",
      "category": "RSA",
      "content": "새로운 RSA 구현 패턴: from Crypto.PublicKey import RSA와 RSA.importKey() 함수 조합으로 사용됩니다. 이는 pycryptodome 라이브러리의 구 버전에서 흔히 발견되는 패턴입니다.",
      "confidence": 0.9,
      "source": "pycryptodome_analysis_2024",
      "keywords": ["RSA.importKey", "Crypto.PublicKey", "pycryptodome"],
      "file_extensions": [".py"],
      "severity": "high"
    },
    {
      "type": "safe_pattern",
      "category": "CRYSTALS-Kyber",
      "content": "양자내성 키 캡슐화: from kyber import Kyber512, Kyber768, Kyber1024 패턴은 NIST 표준 Kyber 구현을 나타냅니다. 이는 양자 컴퓨터 공격에 안전한 키 교환 메커니즘입니다.",
      "confidence": 1.0,
      "source": "NIST_PQC_standard_2024",
      "keywords": ["Kyber512", "Kyber768", "Kyber1024", "kyber"],
      "file_extensions": [".py", ".c", ".cpp"],
      "severity": "safe"
    }
  ]
}
```

#### 바이너리 시그니처 추가

`data/rag_knowledge_base/binary/new_signatures.json`:

```json
{
  "signatures": [
    {
      "type": "binary_signature",
      "category": "OpenSSL_3.x",
      "content": "OpenSSL 3.x에서 새로 도입된 EVP_PKEY_Q_keygen 함수는 간소화된 키 생성 인터페이스입니다. 바이너리에서 이 함수명이 발견되면 최신 OpenSSL을 사용하되 여전히 RSA 등 양자 취약 알고리즘을 사용할 가능성이 있습니다.",
      "confidence": 0.8,
      "source": "openssl_3.x_analysis",
      "keywords": ["EVP_PKEY_Q_keygen", "EVP_PKEY_generate", "OSSL_PARAM"],
      "file_types": ["binary", "shared_library"],
      "severity": "medium"
    },
    {
      "type": "binary_signature",
      "category": "Windows_CNG",
      "content": "Windows CNG (Cryptography Next Generation) API의 BCryptGenerateKeyPair 함수는 Windows 10+ 환경에서 암호화 키 생성에 사용됩니다. BCRYPT_RSA_ALGORITHM, BCRYPT_ECDSA_P256_ALGORITHM 등의 상수와 함께 사용시 양자 취약성을 나타냅니다.",
      "confidence": 0.9,
      "source": "windows_cng_analysis",
      "keywords": ["BCryptGenerateKeyPair", "BCRYPT_RSA_ALGORITHM", "BCRYPT_ECDSA_P256_ALGORITHM"],
      "file_types": ["exe", "dll"],
      "severity": "high"
    }
  ]
}
```

#### 설정 패턴 추가

`data/rag_knowledge_base/parameter/new_configs.json`:

```json
{
  "config_patterns": [
    {
      "type": "config_pattern",
      "category": "JWT_RS512",
      "content": "JWT RS512 알고리즘 설정: 'algorithm': 'RS512' 또는 'alg': 'RS512'는 SHA-512 해시를 사용하는 RSA 서명을 의미합니다. 이는 양자 컴퓨터에 취약하므로 양자내성 서명 알고리즘으로 교체가 필요합니다.",
      "confidence": 1.0,
      "source": "JWT_security_analysis_2024",
      "keywords": ["RS512", "algorithm", "alg"],
      "file_extensions": [".json", ".yaml", ".yml", ".config"],
      "severity": "high"
    },
    {
      "type": "config_pattern",
      "category": "TLS_1.3_ECDHE",
      "content": "TLS 1.3 설정에서 TLS_AES_256_GCM_SHA384 cipher suite는 ECDHE 키 교환을 사용합니다. 대칭 암호화는 안전하지만 키 교환 과정에서 타원곡선 암호화를 사용하므로 양자 취약성이 있습니다.",
      "confidence": 0.8,
      "source": "TLS_1.3_analysis",
      "keywords": ["TLS_AES_256_GCM_SHA384", "TLS_ECDHE", "cipher_suites"],
      "file_extensions": [".conf", ".cfg", ".config"],
      "severity": "medium"
    }
  ]
}
```

#### 로그 패턴 추가

`data/rag_knowledge_base/log_conf/new_log_patterns.json`:

```json
{
  "log_patterns": [
    {
      "type": "log_pattern",
      "category": "SSH_Connection",
      "content": "SSH 연결 로그에서 'Server host key: ecdsa-sha2-nistp384'는 NIST P-384 타원곡선을 사용하는 ECDSA 호스트 키를 나타냅니다. 이는 양자 컴퓨터 공격에 취약하므로 Ed25519 같은 현대적 알고리즘이나 향후 양자내성 서명으로 교체가 권장됩니다.",
      "confidence": 0.9,
      "source": "SSH_log_analysis_2024",
      "keywords": ["ecdsa-sha2-nistp384", "Server host key", "SSH"],
      "log_types": ["ssh", "sshd", "auth"],
      "severity": "medium"
    },
    {
      "type": "log_pattern",
      "category": "Certificate_Validation",
      "content": "인증서 검증 로그에서 'Certificate signature algorithm: sha256WithRSAEncryption'은 SHA-256 해시와 RSA 서명을 사용하는 X.509 인증서를 나타냅니다. RSA는 양자 컴퓨터에 취약하므로 Dilithium 등 양자내성 서명 알고리즘으로의 전환을 고려해야 합니다.",
      "confidence": 1.0,
      "source": "X509_analysis",
      "keywords": ["sha256WithRSAEncryption", "Certificate signature algorithm", "X.509"],
      "log_types": ["ssl", "tls", "cert"],
      "severity": "high"
    }
  ]
}
```

### 방법 2: Python API를 통한 동적 추가

서버 실행 중에 새로운 지식을 동적으로 추가할 수 있습니다.

```python
# scripts/add_knowledge.py
import asyncio
from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def add_new_pattern():
    # 소스코드 에이전트에 새 패턴 추가
    source_manager = await KnowledgeManagerFactory.get_manager("source_code")

    success = await source_manager.add_new_knowledge(
        content="새로운 암호화 패턴: secp256k1 타원곡선은 비트코인에서 사용되는 ECDSA 구현으로, 양자 컴퓨터에 취약합니다.",
        knowledge_type="crypto_pattern",
        category="ECDSA_secp256k1",
        confidence=0.95,
        source="bitcoin_analysis_2024"
    )

    if success:
        print("✅ 새 지식 추가 완료")
    else:
        print("❌ 지식 추가 실패")

if __name__ == "__main__":
    asyncio.run(add_new_pattern())
```

### 방법 3: 대량 데이터 가져오기

외부 데이터베이스나 API에서 대량의 데이터를 가져와 RAG 시스템에 추가할 수 있습니다.

```python
# scripts/bulk_import.py
import asyncio
import json
import requests
from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def import_cve_data():
    """CVE 데이터베이스에서 암호화 관련 취약점 정보 가져오기"""

    # CVE API에서 데이터 가져오기 (예시)
    response = requests.get("https://cve.circl.lu/api/search/cryptography")
    cve_data = response.json()

    source_manager = await KnowledgeManagerFactory.get_manager("source_code")

    for cve in cve_data.get("results", []):
        if "rsa" in cve.get("summary", "").lower():
            await source_manager.add_new_knowledge(
                content=f"CVE-{cve['id']}: {cve['summary']}",
                knowledge_type="vulnerability",
                category="RSA_CVE",
                confidence=0.8,
                source=f"CVE-{cve['id']}"
            )

    print(f"✅ {len(cve_data.get('results', []))}개 CVE 데이터 가져오기 완료")

if __name__ == "__main__":
    asyncio.run(import_cve_data())
```

## 🔄 데이터 업데이트 및 관리

### 지식 베이스 새로고침

새로운 JSON 파일을 추가한 후 지식 베이스를 새로고침하려면:

```python
# scripts/refresh_knowledge.py
import asyncio
from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def refresh_all_knowledge():
    agent_types = ["source_code", "binary", "parameter", "log_conf"]

    for agent_type in agent_types:
        manager = await KnowledgeManagerFactory.get_manager(agent_type)

        # 강제 재로딩 (force_reload=True)
        success = await manager.initialize_knowledge_base(force_reload=True)

        if success:
            collection_info = manager.vector_store.get_collection_info()
            print(f"✅ {agent_type}: {collection_info['document_count']}개 문서 로드됨")
        else:
            print(f"❌ {agent_type}: 로딩 실패")

if __name__ == "__main__":
    asyncio.run(refresh_all_knowledge())
```

### 벡터 데이터베이스 관리

```python
# scripts/manage_vectordb.py
import asyncio
from pqc_inspector_server.services.vector_store import VectorStoreFactory

async def get_db_status():
    """모든 벡터 데이터베이스 상태 확인"""
    agent_types = ["source_code", "binary", "parameter", "log_conf"]

    for agent_type in agent_types:
        store = VectorStoreFactory.get_store(agent_type)
        info = store.get_collection_info()
        print(f"{agent_type}: {info}")

async def clear_specific_db(agent_type: str):
    """특정 에이전트의 벡터 DB 초기화"""
    store = VectorStoreFactory.get_store(agent_type)
    success = store.clear_collection()

    if success:
        print(f"✅ {agent_type} 벡터 DB 초기화 완료")
    else:
        print(f"❌ {agent_type} 벡터 DB 초기화 실패")

if __name__ == "__main__":
    # 상태 확인
    asyncio.run(get_db_status())

    # 특정 DB 초기화 (주의: 모든 데이터 삭제됨)
    # asyncio.run(clear_specific_db("source_code"))
```

## 📊 지식 베이스 품질 관리

### 데이터 품질 체크

```python
# scripts/quality_check.py
import asyncio
from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

async def check_knowledge_quality():
    """지식 베이스의 품질을 확인합니다"""

    agent_types = ["source_code", "binary", "parameter", "log_conf"]

    for agent_type in agent_types:
        manager = await KnowledgeManagerFactory.get_manager(agent_type)

        # 테스트 쿼리로 검색 품질 확인
        test_queries = {
            "source_code": "RSA encryption python",
            "binary": "OpenSSL RSA function",
            "parameter": "JWT RS256 algorithm",
            "log_conf": "TLS handshake cipher"
        }

        query = test_queries.get(agent_type, "cryptography")
        result = await manager.search_relevant_context(query, top_k=3)

        print(f"\n🧪 {agent_type} 품질 테스트:")
        print(f"  쿼리: {query}")
        print(f"  평균 유사도: {result.get('confidence', 0):.3f}")
        print(f"  검색된 컨텍스트 수: {len(result.get('contexts', []))}")

        for i, ctx in enumerate(result.get('contexts', [])[:2]):
            print(f"  [{i+1}] {ctx['category']} (유사도: {ctx['similarity']:.3f})")

if __name__ == "__main__":
    asyncio.run(check_knowledge_quality())
```

## 🎯 최적화 팁

### 1. 임베딩 최적화

```python
# 효과적인 지식 베이스 컨텐츠 작성법
good_content = """
RSA 2048-bit 키 생성: rsa.generate_private_key(65537, 2048) 함수는
pyCryptography 라이브러리에서 RSA 개인키를 생성합니다.
이는 양자 컴퓨터에 취약하므로 CRYSTALS-Kyber로 교체 권장.
"""

# 피해야 할 방식
bad_content = """
RSA는 나쁘다. 사용하지 마라.
"""
```

### 2. 카테고리 분류

- **crypto_pattern**: 특정 암호화 알고리즘 사용 패턴
- **safe_pattern**: 양자내성 알고리즘 사용 패턴
- **library_pattern**: 라이브러리별 특화 패턴
- **vulnerability**: 알려진 취약점 정보
- **binary_signature**: 바이너리에서 발견되는 시그니처
- **config_pattern**: 설정 파일 패턴
- **log_pattern**: 로그 파일 패턴

### 3. 신뢰도 점수 가이드라인

- **1.0**: NIST 표준, 공식 문서 기반
- **0.9**: 검증된 보안 연구 결과
- **0.8**: 실증적 분석 결과
- **0.7**: 경험적 패턴
- **0.6 이하**: 추정 또는 실험적 정보

## 🚀 고급 활용

### 실시간 지식 업데이트

```python
# scripts/auto_update.py
import asyncio
import schedule
import time
from datetime import datetime

async def daily_knowledge_update():
    """매일 자동으로 지식 베이스 업데이트"""
    print(f"🔄 {datetime.now()}: 지식 베이스 자동 업데이트 시작")

    # 1. 외부 API에서 최신 CVE 정보 가져오기
    await import_cve_data()

    # 2. GitHub에서 최신 암호화 패턴 수집
    await collect_github_patterns()

    # 3. 지식 베이스 새로고침
    await refresh_all_knowledge()

    print("✅ 자동 업데이트 완료")

# 스케줄 설정
schedule.every().day.at("02:00").do(lambda: asyncio.run(daily_knowledge_update()))

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
```

### 커뮤니티 기여 시스템

```python
# scripts/community_submission.py
async def submit_community_knowledge(user_data):
    """사용자가 제출한 지식을 검토 후 추가"""

    # 1. 데이터 검증
    if validate_submission(user_data):
        # 2. 임시 저장
        temp_id = save_to_pending(user_data)

        # 3. 전문가 검토 요청
        await request_expert_review(temp_id)

        return {"status": "pending_review", "id": temp_id}
    else:
        return {"status": "validation_failed"}
```

이 가이드를 따라 PQC Inspector의 RAG 시스템을 지속적으로 개선하고 확장할 수 있습니다. 새로운 암호화 위협과 패턴이 발견될 때마다 지식 베이스를 업데이트하여 시스템의 탐지 능력을 향상시키세요!