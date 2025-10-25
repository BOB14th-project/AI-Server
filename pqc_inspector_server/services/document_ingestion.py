# File: pqc_inspector_server/services/document_ingestion.py
# 📚 문서를 RAG 시스템에 수집하는 파이프라인입니다.

import asyncio
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .document_processor import DocumentProcessor, get_document_processor
from .knowledge_manager import KnowledgeManagerFactory
from .embedding_service import get_embedding_service

class DocumentIngestionPipeline:
    def __init__(self):
        self.processor = get_document_processor()
        self.embedding_service = get_embedding_service()
        self.supported_agents = ["source_code", "assembly_binary", "logs_config"]

    async def ingest_single_document(
        self,
        file_path: str,
        agent_type: str = "auto",
        source_name: Optional[str] = None,
        confidence: float = 0.9
    ) -> Dict[str, Any]:
        """
        단일 문서를 RAG 시스템에 수집합니다.
        """
        try:
            print(f"📚 문서 수집 시작: {file_path}")

            # 1. 문서 처리
            processed_doc = await self.processor.process_document(file_path, agent_type)

            # 2. 소스명 설정
            if not source_name:
                source_name = f"document_{Path(file_path).stem}"

            # 3. 에이전트 타입 검증
            final_agent_type = processed_doc["agent_type"]
            if final_agent_type not in self.supported_agents:
                final_agent_type = "source_code"  # 기본값

            # 4. 지식 매니저 가져오기
            knowledge_manager = await KnowledgeManagerFactory.get_manager(final_agent_type)

            # 5. 청크별로 임베딩 생성 및 저장
            success_count = 0
            total_chunks = len(processed_doc["chunks"])

            print(f"🔄 {total_chunks}개 청크를 {final_agent_type} 에이전트에 추가 중...")

            for chunk in processed_doc["chunks"]:
                try:
                    # 메타데이터 생성
                    metadata = self._create_chunk_metadata(
                        chunk, processed_doc["file_info"], source_name, confidence
                    )

                    # 지식 베이스에 추가
                    success = await knowledge_manager.add_new_knowledge(
                        content=chunk["content"],
                        knowledge_type="document_chunk",
                        category=f"doc_{Path(file_path).stem}",
                        confidence=confidence,
                        source=source_name
                    )

                    if success:
                        success_count += 1
                    else:
                        print(f"⚠️ 청크 {chunk['index']} 추가 실패")

                except Exception as e:
                    print(f"❌ 청크 {chunk['index']} 처리 중 오류: {e}")

            # 6. 결과 반환
            result = {
                "success": success_count > 0,
                "file_path": file_path,
                "agent_type": final_agent_type,
                "total_chunks": total_chunks,
                "success_chunks": success_count,
                "failed_chunks": total_chunks - success_count,
                "source_name": source_name,
                "document_info": processed_doc["file_info"],
                "ingestion_time": datetime.now().isoformat()
            }

            if success_count > 0:
                print(f"✅ 문서 수집 완료: {success_count}/{total_chunks} 청크 성공")
            else:
                print(f"❌ 문서 수집 실패: 모든 청크 추가 실패")

            return result

        except Exception as e:
            print(f"❌ 문서 수집 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "ingestion_time": datetime.now().isoformat()
            }

    async def ingest_directory(
        self,
        directory_path: str,
        agent_type: str = "auto",
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        디렉토리의 모든 지원 파일을 RAG 시스템에 수집합니다.
        """
        try:
            directory = Path(directory_path)
            if not directory.exists():
                raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {directory_path}")

            print(f"📁 디렉토리 수집 시작: {directory_path}")

            # 지원 파일 찾기
            files = self._find_supported_files(directory, recursive, file_patterns)

            if not files:
                print("⚠️ 지원하는 문서 파일을 찾을 수 없습니다")
                return {
                    "success": False,
                    "message": "지원하는 문서 파일 없음",
                    "total_files": 0
                }

            print(f"📄 {len(files)}개 파일 발견")

            # 각 파일 처리
            results = []
            success_count = 0

            for file_path in files:
                print(f"\n처리 중: {file_path.name}")
                result = await self.ingest_single_document(
                    str(file_path),
                    agent_type,
                    source_name=f"directory_{file_path.stem}"
                )
                results.append(result)

                if result["success"]:
                    success_count += 1

            # 전체 결과 요약
            summary = {
                "success": success_count > 0,
                "directory_path": directory_path,
                "total_files": len(files),
                "success_files": success_count,
                "failed_files": len(files) - success_count,
                "file_results": results,
                "ingestion_time": datetime.now().isoformat()
            }

            print(f"\n📊 디렉토리 수집 완료: {success_count}/{len(files)} 파일 성공")
            return summary

        except Exception as e:
            print(f"❌ 디렉토리 수집 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "directory_path": directory_path,
                "ingestion_time": datetime.now().isoformat()
            }

    async def ingest_batch_files(
        self,
        file_paths: List[str],
        agent_type: str = "auto",
        source_prefix: str = "batch"
    ) -> Dict[str, Any]:
        """
        여러 파일을 배치로 RAG 시스템에 수집합니다.
        """
        print(f"📦 배치 수집 시작: {len(file_paths)}개 파일")

        results = []
        success_count = 0

        for i, file_path in enumerate(file_paths):
            print(f"\n[{i+1}/{len(file_paths)}] 처리 중: {Path(file_path).name}")

            result = await self.ingest_single_document(
                file_path,
                agent_type,
                source_name=f"{source_prefix}_{Path(file_path).stem}"
            )
            results.append(result)

            if result["success"]:
                success_count += 1

        summary = {
            "success": success_count > 0,
            "total_files": len(file_paths),
            "success_files": success_count,
            "failed_files": len(file_paths) - success_count,
            "file_results": results,
            "ingestion_time": datetime.now().isoformat()
        }

        print(f"\n📊 배치 수집 완료: {success_count}/{len(file_paths)} 파일 성공")
        return summary

    async def ingest_agent_directories(
        self,
        documents_root: str = "data/documents",
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        에이전트별 디렉토리 구조에서 모든 문서를 수집합니다.
        documents_root/source_code/, documents_root/binary/ 등의 구조를 처리합니다.
        """
        print(f"🗂️ 에이전트별 디렉토리 수집 시작: {documents_root}")

        documents_path = Path(documents_root)
        if not documents_path.exists():
            raise FileNotFoundError(f"문서 루트 디렉토리를 찾을 수 없습니다: {documents_root}")

        overall_results = {
            "success": False,
            "documents_root": documents_root,
            "agent_results": {},
            "total_files": 0,
            "total_success": 0,
            "total_failed": 0,
            "ingestion_time": datetime.now().isoformat()
        }

        total_success = 0
        total_files = 0

        for agent_type in self.supported_agents:
            agent_dir = documents_path / agent_type

            if not agent_dir.exists():
                print(f"⚠️ {agent_type} 디렉토리가 없습니다: {agent_dir}")
                overall_results["agent_results"][agent_type] = {
                    "success": False,
                    "message": "디렉토리 없음",
                    "total_files": 0
                }
                continue

            print(f"\n📁 {agent_type} 디렉토리 처리 중...")

            # 해당 에이전트 디렉토리의 모든 파일 수집
            agent_result = await self.ingest_directory(
                str(agent_dir),
                agent_type=agent_type,  # 에이전트 타입 명시적 지정
                recursive=recursive
            )

            overall_results["agent_results"][agent_type] = agent_result

            if agent_result["success"]:
                total_success += agent_result["success_files"]
            total_files += agent_result["total_files"]

        overall_results["total_files"] = total_files
        overall_results["total_success"] = total_success
        overall_results["total_failed"] = total_files - total_success
        overall_results["success"] = total_success > 0

        print(f"\n🎯 전체 에이전트별 수집 완료:")
        print(f"  총 파일: {total_files}")
        print(f"  성공: {total_success}")
        print(f"  실패: {total_files - total_success}")

        for agent_type, result in overall_results["agent_results"].items():
            if result.get("total_files", 0) > 0:
                print(f"  {agent_type}: {result.get('success_files', 0)}/{result.get('total_files', 0)} 성공")

        return overall_results

    def _find_supported_files(
        self,
        directory: Path,
        recursive: bool,
        file_patterns: Optional[List[str]]
    ) -> List[Path]:
        """지원하는 파일들을 찾습니다."""
        files = []

        # 검색 패턴 설정
        if recursive:
            search_pattern = "**/*"
        else:
            search_pattern = "*"

        # 모든 파일 찾기
        for file_path in directory.glob(search_pattern):
            if file_path.is_file() and self.processor.is_supported(str(file_path)):
                # 패턴 필터링
                if file_patterns:
                    if any(pattern in file_path.name for pattern in file_patterns):
                        files.append(file_path)
                else:
                    files.append(file_path)

        return files

    def _create_chunk_metadata(
        self,
        chunk: Dict[str, Any],
        file_info: Dict[str, Any],
        source_name: str,
        confidence: float
    ) -> Dict[str, Any]:
        """청크 메타데이터를 생성합니다."""
        return {
            "chunk_index": chunk["index"],
            "chunk_hash": chunk["chunk_hash"],
            "char_count": chunk["char_count"],
            "word_count": chunk["word_count"],
            "source_file": file_info["filename"],
            "file_size": file_info["file_size"],
            "file_hash": file_info["file_hash"],
            "source_name": source_name,
            "confidence": confidence,
            "ingestion_time": datetime.now().isoformat()
        }

    async def validate_ingestion(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """수집 결과를 검증합니다."""
        if not result.get("success"):
            return {"valid": False, "reason": "수집 실패"}

        agent_type = result.get("agent_type")
        source_name = result.get("source_name")

        if not agent_type or not source_name:
            return {"valid": False, "reason": "필수 정보 누락"}

        try:
            # 지식 매니저에서 실제로 검색해보기
            knowledge_manager = await KnowledgeManagerFactory.get_manager(agent_type)
            search_result = await knowledge_manager.search_relevant_context(
                query=source_name,
                top_k=1
            )

            if search_result.get("contexts"):
                return {
                    "valid": True,
                    "found_chunks": len(search_result["contexts"]),
                    "avg_confidence": search_result.get("confidence", 0)
                }
            else:
                return {"valid": False, "reason": "검색 결과 없음"}

        except Exception as e:
            return {"valid": False, "reason": f"검증 중 오류: {e}"}

# 의존성 주입을 위한 함수
def get_document_ingestion_pipeline():
    return DocumentIngestionPipeline()