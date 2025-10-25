# File: pqc_inspector_server/services/knowledge_manager.py
# 📚 각 에이전트별 지식 베이스를 관리하고 검색하는 서비스입니다.

from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
from .embedding_service import EmbeddingService, get_embedding_service
import os
import json

class KnowledgeManager:
    def __init__(self, agent_type: str, vector_store: VectorStore):
        self.agent_type = agent_type
        self.vector_store = vector_store
        self.embedding_service = get_embedding_service()
        self.knowledge_base_path = f"data/rag_knowledge_base/{agent_type}"
        print(f"📚 {agent_type} KnowledgeManager 초기화됨")

    async def initialize_knowledge_base(self, force_reload: bool = False) -> bool:
        """
        지식 베이스를 초기화합니다.
        """
        try:
            # 이미 데이터가 있고 강제 재로딩이 아니면 스킵
            collection_info = self.vector_store.get_collection_info()
            if collection_info["document_count"] > 0 and not force_reload:
                print(f"✅ {self.agent_type} 지식 베이스가 이미 로드됨 ({collection_info['document_count']}개 문서)")
                return True

            if force_reload:
                self.vector_store.clear_collection()

            # 기본 지식 베이스 로드
            success = await self._load_default_knowledge()

            if success:
                print(f"✅ {self.agent_type} 지식 베이스 초기화 완료")
            else:
                print(f"⚠️ {self.agent_type} 지식 베이스 초기화 실패")

            return success

        except Exception as e:
            print(f"❌ 지식 베이스 초기화 중 오류: {e}")
            return False

    async def _load_default_knowledge(self) -> bool:
        """
        기본 지식 베이스와 JSON 파일들을 로드합니다.
        """
        # 1. 기본 하드코딩된 지식 로드
        knowledge_data = self._get_default_knowledge_for_agent()

        # 2. JSON 파일에서 추가 지식 로드
        json_knowledge = await self._load_json_knowledge()
        knowledge_data.extend(json_knowledge)

        if not knowledge_data:
            print(f"⚠️ {self.agent_type}에 대한 지식이 없습니다.")
            return True  # 빈 지식 베이스도 유효함

        documents = []
        metadatas = []

        for item in knowledge_data:
            documents.append(item["content"])
            metadatas.append({
                "type": item["type"],
                "category": item["category"],
                "confidence": item.get("confidence", 1.0),
                "source": item.get("source", "default")
            })

        if documents:
            # 임베딩 생성
            embeddings = await self.embedding_service.create_embeddings(documents)

            if embeddings:
                # 벡터 DB에 저장
                success = await self.vector_store.add_documents(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                return success

        return False

    async def _load_json_knowledge(self) -> List[Dict[str, Any]]:
        """JSON 파일들에서 지식을 로드합니다."""
        import json
        import os
        from pathlib import Path

        knowledge_data = []
        json_dir = Path(self.knowledge_base_path)

        if not json_dir.exists():
            os.makedirs(json_dir, exist_ok=True)
            return knowledge_data

        # JSON 파일들 찾기
        for json_file in json_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 데이터 구조에 따라 처리
                items = []
                if 'patterns' in data:
                    items = data['patterns']
                elif 'signatures' in data:
                    items = data['signatures']
                elif 'config_patterns' in data:
                    items = data['config_patterns']
                elif 'log_patterns' in data:
                    items = data['log_patterns']
                elif isinstance(data, list):
                    items = data
                else:
                    items = [data]

                # 각 아이템을 표준 형식으로 변환
                for item in items:
                    if isinstance(item, dict) and 'content' in item:
                        knowledge_data.append({
                            "type": item.get("type", "knowledge"),
                            "category": item.get("category", "general"),
                            "content": item["content"],
                            "confidence": item.get("confidence", 0.8),
                            "source": f"json_{json_file.stem}"
                        })

                print(f"✅ JSON 파일 로드됨: {json_file.name} ({len(items)}개 항목)")

            except Exception as e:
                print(f"❌ JSON 파일 로드 실패 {json_file.name}: {e}")

        return knowledge_data

    def _get_default_knowledge_for_agent(self) -> List[Dict[str, Any]]:
        """
        에이전트별 기본 지식을 반환합니다.
        """
        if self.agent_type == "source_code":
            return self._get_source_code_knowledge()
        elif self.agent_type == "binary":
            return self._get_binary_knowledge()
        elif self.agent_type == "log_conf":
            return self._get_log_conf_knowledge()
        else:
            return []

    def _get_source_code_knowledge(self) -> List[Dict[str, Any]]:
        """소스코드 분석을 위한 지식 베이스"""
        return [
            {
                "type": "crypto_pattern",
                "category": "RSA",
                "content": "RSA 암호화는 양자 컴퓨터에 취약합니다. from cryptography.hazmat.primitives.asymmetric import rsa 또는 import rsa 패턴으로 사용됩니다. RSA.generate(), rsa.newkeys(), RSA_generate_key() 함수들이 주요 탐지 포인트입니다.",
                "confidence": 1.0,
                "source": "NIST_PQC_guidelines"
            },
            {
                "type": "crypto_pattern",
                "category": "ECDSA",
                "content": "ECDSA(타원곡선 디지털 서명)는 양자 컴퓨터에 취약합니다. from cryptography.hazmat.primitives.asymmetric import ec, from ecdsa import SigningKey 패턴으로 사용됩니다. ec.generate_private_key(), SigningKey.generate() 함수들을 탐지해야 합니다.",
                "confidence": 1.0,
                "source": "NIST_PQC_guidelines"
            },
            {
                "type": "crypto_pattern",
                "category": "DSA",
                "content": "DSA(디지털 서명 알고리즘)는 양자 컴퓨터에 취약합니다. from cryptography.hazmat.primitives.asymmetric import dsa 패턴으로 사용됩니다. dsa.generate_private_key() 함수를 탐지해야 합니다.",
                "confidence": 1.0,
                "source": "NIST_PQC_guidelines"
            },
            {
                "type": "crypto_pattern",
                "category": "DH",
                "content": "Diffie-Hellman 키 교환은 양자 컴퓨터에 취약합니다. from cryptography.hazmat.primitives.asymmetric import dh 패턴으로 사용됩니다. dh.generate_private_key(), DH_generate_key() 함수들을 탐지해야 합니다.",
                "confidence": 1.0,
                "source": "NIST_PQC_guidelines"
            },
            {
                "type": "safe_pattern",
                "category": "PQC",
                "content": "양자내성 암호화 패턴: Kyber (키 캡슐화), Dilithium (디지털 서명), SPHINCS+ (서명), FALCON (서명). 이들은 NIST PQC 표준으로 승인된 양자내성 알고리즘입니다.",
                "confidence": 1.0,
                "source": "NIST_PQC_standards"
            },
            {
                "type": "library_pattern",
                "category": "Python",
                "content": "Python 암호화 라이브러리들: pycryptodome, cryptography, pyOpenSSL, ecdsa, rsa. 이들 라이브러리 import 시 비양자내성 암호화 사용 가능성이 높습니다.",
                "confidence": 0.8,
                "source": "library_analysis"
            }
        ]

    def _get_binary_knowledge(self) -> List[Dict[str, Any]]:
        """바이너리 분석을 위한 지식 베이스"""
        return [
            {
                "type": "binary_signature",
                "category": "OpenSSL",
                "content": "OpenSSL 바이너리 시그니처: RSA_public_encrypt, RSA_private_decrypt, ECDSA_sign, ECDSA_verify 함수명들이 바이너리에서 발견될 수 있습니다. 이들은 양자 취약 암호화를 나타냅니다.",
                "confidence": 0.9,
                "source": "binary_analysis"
            },
            {
                "type": "binary_signature",
                "category": "Windows_CryptoAPI",
                "content": "Windows CryptoAPI 시그니처: CryptGenKey, CryptCreateHash, CryptSignHash, CryptVerifySignature. AT_KEYEXCHANGE, AT_SIGNATURE 플래그와 함께 사용될 때 비양자내성 암호화를 나타냅니다.",
                "confidence": 0.8,
                "source": "windows_crypto_analysis"
            },
            {
                "type": "binary_signature",
                "category": "Constants",
                "content": "암호화 상수들: RSA 지수 65537(0x10001), ECDSA 곡선 파라미터들, DH 소수들. 이런 상수들이 바이너리에 하드코딩되어 있으면 해당 암호화 알고리즘 사용을 의미합니다.",
                "confidence": 0.7,
                "source": "crypto_constants"
            }
        ]

    def _get_log_conf_knowledge(self) -> List[Dict[str, Any]]:
        """로그/설정 분석을 위한 지식 베이스"""
        return [
            {
                "type": "log_pattern",
                "category": "TLS_handshake",
                "content": "TLS 핸드셰이크 로그 패턴: 'Cipher suite: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384', 'Certificate signature algorithm: sha256WithRSAEncryption'. 이런 로그는 양자 취약 암호화 사용을 나타냅니다.",
                "confidence": 0.9,
                "source": "TLS_log_analysis"
            },
            {
                "type": "log_pattern",
                "category": "Certificate",
                "content": "인증서 관련 로그: 'RSA public key', 'ECDSA public key', 'signature algorithm: RSA'. 인증서 생성, 검증, 만료 로그에서 이런 패턴들을 탐지해야 합니다.",
                "confidence": 0.8,
                "source": "certificate_analysis"
            },
            {
                "type": "log_pattern",
                "category": "SSH",
                "content": "SSH 로그 패턴: 'Server host key: ssh-rsa', 'User authentication method: publickey (ssh-rsa)'. SSH 연결 로그에서 양자 취약 키 타입들을 탐지합니다.",
                "confidence": 0.8,
                "source": "SSH_log_analysis"
            },
            {
                "type": "config_pattern",
                "category": "JWT",
                "content": "JWT 알고리즘 설정: RS256, RS384, RS512, ES256, ES384, ES512, PS256, PS384, PS512는 모두 양자 취약 알고리즘입니다. 설정 파일에서 'algorithm': 'RS256' 같은 패턴을 탐지해야 합니다.",
                "confidence": 1.0,
                "source": "JWT_RFC"
            },
            {
                "type": "config_pattern",
                "category": "TLS",
                "content": "TLS 설정에서 양자 취약 cipher suite들: RSA 키 교환, ECDHE-RSA, ECDHE-ECDSA, DHE-RSA. ssl_cipher_list, cipher_suites 설정에서 이런 값들을 탐지해야 합니다.",
                "confidence": 1.0,
                "source": "TLS_standards"
            },
            {
                "type": "config_pattern",
                "category": "SSH",
                "content": "SSH 설정의 양자 취약 요소들: ssh-rsa, ecdsa-sha2-nistp256, ssh-dss 등의 호스트 키 타입. PubkeyAcceptedKeyTypes, HostKeyAlgorithms 설정에서 탐지됩니다.",
                "confidence": 1.0,
                "source": "SSH_RFC"
            }
        ]

    async def search_relevant_context(
        self,
        query: str,
        top_k: int = 3,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        쿼리와 관련된 컨텍스트를 검색합니다.
        """
        try:
            # 쿼리 전처리
            if self.agent_type == "source_code":
                processed_query = self.embedding_service.preprocess_code(query)
            elif self.agent_type == "log_conf":
                processed_query = self.embedding_service.preprocess_config(query)
            else:
                processed_query = query

            # 쿼리 임베딩 생성
            query_embedding = await self.embedding_service.create_single_embedding(processed_query)

            if not query_embedding:
                return {"contexts": [], "confidence": 0.0}

            # 카테고리 필터 설정
            where_filter = {"category": category_filter} if category_filter else None

            # 벡터 검색
            search_results = await self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                where_filter=where_filter
            )

            # 결과 포맷팅
            contexts = []
            for i, doc in enumerate(search_results["documents"]):
                distance = search_results["distances"][i] if i < len(search_results["distances"]) else 1.0
                metadata = search_results["metadatas"][i] if i < len(search_results["metadatas"]) else {}

                contexts.append({
                    "content": doc,
                    "similarity": 1.0 - distance,  # 거리를 유사도로 변환
                    "category": metadata.get("category", "unknown"),
                    "type": metadata.get("type", "unknown"),
                    "source": metadata.get("source", "unknown")
                })

            # 평균 신뢰도 계산
            avg_confidence = sum(ctx["similarity"] for ctx in contexts) / len(contexts) if contexts else 0.0

            return {
                "contexts": contexts,
                "confidence": avg_confidence,
                "query_processed": processed_query
            }

        except Exception as e:
            print(f"❌ 컨텍스트 검색 중 오류: {e}")
            return {"contexts": [], "confidence": 0.0}

    async def add_new_knowledge(
        self,
        content: str,
        knowledge_type: str,
        category: str,
        confidence: float = 1.0,
        source: str = "user_input",
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        새로운 지식을 추가합니다.
        """
        try:
            # 임베딩 생성
            embedding = await self.embedding_service.create_single_embedding(content)

            if not embedding:
                return False

            # 메타데이터 생성
            metadata = {
                "type": knowledge_type,
                "category": category,
                "confidence": confidence,
                "source": source
            }

            # 추가 메타데이터 병합
            if additional_metadata:
                metadata.update(additional_metadata)

            # 벡터 DB에 추가
            success = await self.vector_store.add_documents(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata]
            )

            if success:
                print(f"✅ 새 지식 추가됨: {category} - {knowledge_type}")

            return success

        except Exception as e:
            print(f"❌ 지식 추가 중 오류: {e}")
            return False

# 의존성 주입을 위한 팩토리
class KnowledgeManagerFactory:
    _instances = {}

    @classmethod
    async def get_manager(cls, agent_type: str) -> KnowledgeManager:
        """
        에이전트 타입별 지식 매니저를 반환합니다.
        """
        if agent_type not in cls._instances:
            from .vector_store import VectorStoreFactory
            vector_store = VectorStoreFactory.get_store(agent_type)
            manager = KnowledgeManager(agent_type, vector_store)

            # 지식 베이스 초기화
            await manager.initialize_knowledge_base()

            cls._instances[agent_type] = manager

        return cls._instances[agent_type]

# 각 에이전트별 의존성 주입 함수
async def get_source_code_knowledge_manager() -> KnowledgeManager:
    return await KnowledgeManagerFactory.get_manager("source_code")

async def get_binary_knowledge_manager() -> KnowledgeManager:
    return await KnowledgeManagerFactory.get_manager("binary")

async def get_log_conf_knowledge_manager() -> KnowledgeManager:
    return await KnowledgeManagerFactory.get_manager("log_conf")