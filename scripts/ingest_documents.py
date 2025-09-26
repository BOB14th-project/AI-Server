#!/usr/bin/env python3
"""
문서 수집 스크립트
공식 문서, PDF, DOCX 등을 RAG 시스템에 직접 추가하는 도구

사용법:
  python scripts/ingest_documents.py file path/to/document.pdf [agent_type]
  python scripts/ingest_documents.py directory path/to/docs/ [agent_type]
  python scripts/ingest_documents.py batch file1.pdf file2.docx file3.md
"""

import asyncio
import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pqc_inspector_server.services.document_ingestion import get_document_ingestion_pipeline
from pqc_inspector_server.services.document_processor import get_document_processor

class DocumentIngestionCLI:
    def __init__(self):
        self.pipeline = get_document_ingestion_pipeline()
        self.processor = get_document_processor()

    async def ingest_single_file(self, file_path: str, agent_type: str = "auto"):
        """단일 파일을 수집합니다."""
        print(f"📄 단일 파일 수집: {file_path}")

        if not Path(file_path).exists():
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            return False

        if not self.processor.is_supported(file_path):
            print(f"❌ 지원하지 않는 파일 형식: {Path(file_path).suffix}")
            print(f"지원 형식: {self.processor.supported_formats}")
            return False

        try:
            result = await self.pipeline.ingest_single_document(file_path, agent_type)

            if result["success"]:
                print(f"\n✅ 수집 성공!")
                print(f"  파일: {result['file_path']}")
                print(f"  에이전트: {result['agent_type']}")
                print(f"  총 청크: {result['total_chunks']}")
                print(f"  성공 청크: {result['success_chunks']}")
                print(f"  실패 청크: {result['failed_chunks']}")
                return True
            else:
                print(f"\n❌ 수집 실패!")
                if "error" in result:
                    print(f"  오류: {result['error']}")
                return False

        except Exception as e:
            print(f"❌ 수집 중 오류: {e}")
            return False

    async def ingest_directory(self, directory_path: str, agent_type: str = "auto", recursive: bool = True):
        """디렉토리의 모든 문서를 수집합니다."""
        print(f"📁 디렉토리 수집: {directory_path}")
        print(f"  재귀 검색: {recursive}")

        try:
            result = await self.pipeline.ingest_directory(
                directory_path,
                agent_type,
                recursive
            )

            if result["success"]:
                print(f"\n✅ 디렉토리 수집 성공!")
                print(f"  디렉토리: {result['directory_path']}")
                print(f"  총 파일: {result['total_files']}")
                print(f"  성공 파일: {result['success_files']}")
                print(f"  실패 파일: {result['failed_files']}")

                # 개별 파일 결과 요약
                print(f"\n📊 파일별 결과:")
                for file_result in result['file_results']:
                    status = "✅" if file_result['success'] else "❌"
                    file_name = Path(file_result['file_path']).name
                    chunks = f"{file_result.get('success_chunks', 0)}/{file_result.get('total_chunks', 0)}"
                    print(f"  {status} {file_name} ({chunks} 청크)")

                return True
            else:
                print(f"\n❌ 디렉토리 수집 실패!")
                if "error" in result:
                    print(f"  오류: {result['error']}")
                return False

        except Exception as e:
            print(f"❌ 디렉토리 수집 중 오류: {e}")
            return False

    async def ingest_batch_files(self, file_paths: list, agent_type: str = "auto"):
        """여러 파일을 배치로 수집합니다."""
        print(f"📦 배치 수집: {len(file_paths)}개 파일")

        # 파일 존재 확인
        valid_files = []
        for file_path in file_paths:
            if Path(file_path).exists():
                if self.processor.is_supported(file_path):
                    valid_files.append(file_path)
                else:
                    print(f"⚠️ 지원하지 않는 형식: {file_path}")
            else:
                print(f"⚠️ 파일 없음: {file_path}")

        if not valid_files:
            print("❌ 유효한 파일이 없습니다.")
            return False

        print(f"📋 유효한 파일: {len(valid_files)}개")

        try:
            result = await self.pipeline.ingest_batch_files(valid_files, agent_type)

            if result["success"]:
                print(f"\n✅ 배치 수집 성공!")
                print(f"  총 파일: {result['total_files']}")
                print(f"  성공 파일: {result['success_files']}")
                print(f"  실패 파일: {result['failed_files']}")

                # 개별 파일 결과
                print(f"\n📊 파일별 결과:")
                for file_result in result['file_results']:
                    status = "✅" if file_result['success'] else "❌"
                    file_name = Path(file_result['file_path']).name
                    chunks = f"{file_result.get('success_chunks', 0)}/{file_result.get('total_chunks', 0)}"
                    print(f"  {status} {file_name} ({chunks} 청크)")

                return True
            else:
                print(f"\n❌ 배치 수집 실패!")
                return False

        except Exception as e:
            print(f"❌ 배치 수집 중 오류: {e}")
            return False

    def show_supported_formats(self):
        """지원하는 파일 형식을 표시합니다."""
        print("📋 지원하는 파일 형식:")
        print(f"  {', '.join(self.processor.supported_formats)}")

        print("\n📚 라이브러리 요구사항:")
        print("  PDF: pip install PyMuPDF")
        print("  DOCX: pip install python-docx")
        print("  Markdown: pip install markdown beautifulsoup4")

    async def ingest_agent_directories(self, documents_root: str = "data/documents", recursive: bool = True):
        """에이전트별 디렉토리 구조에서 모든 문서를 수집합니다."""
        print(f"🗂️ 에이전트별 디렉토리 수집: {documents_root}")

        try:
            result = await self.pipeline.ingest_agent_directories(documents_root, recursive)

            if result["success"]:
                print(f"\n✅ 에이전트별 수집 성공!")
                print(f"  문서 루트: {result['documents_root']}")
                print(f"  총 파일: {result['total_files']}")
                print(f"  성공: {result['total_success']}")
                print(f"  실패: {result['total_failed']}")

                print(f"\n📊 에이전트별 결과:")
                for agent_type, agent_result in result['agent_results'].items():
                    if agent_result.get('total_files', 0) > 0:
                        status = "✅" if agent_result.get('success', False) else "❌"
                        success = agent_result.get('success_files', 0)
                        total = agent_result.get('total_files', 0)
                        print(f"  {status} {agent_type}: {success}/{total} 파일")
                    else:
                        print(f"  ⚪ {agent_type}: 파일 없음")

                return True
            else:
                print(f"\n❌ 에이전트별 수집 실패!")
                if "error" in result:
                    print(f"  오류: {result['error']}")
                return False

        except Exception as e:
            print(f"❌ 에이전트별 수집 중 오류: {e}")
            return False

    async def validate_ingestion(self, file_paths: list):
        """수집된 문서들이 정상적으로 검색되는지 확인합니다."""
        print("🔍 수집 검증 시작...")

        for file_path in file_paths:
            file_name = Path(file_path).stem
            print(f"\n테스트: {file_name}")

            # 각 에이전트에서 검색 테스트
            from pqc_inspector_server.services.knowledge_manager import KnowledgeManagerFactory

            for agent_type in ["source_code", "binary", "parameter", "log_conf"]:
                try:
                    manager = await KnowledgeManagerFactory.get_manager(agent_type)
                    result = await manager.search_relevant_context(file_name, top_k=1)

                    if result.get('contexts'):
                        confidence = result.get('confidence', 0)
                        print(f"  ✅ {agent_type}: 검색됨 (신뢰도: {confidence:.3f})")
                    else:
                        print(f"  ⚪ {agent_type}: 검색 안됨")

                except Exception as e:
                    print(f"  ❌ {agent_type}: 오류 - {e}")


async def main():
    parser = argparse.ArgumentParser(description="문서를 RAG 시스템에 수집합니다")
    parser.add_argument("command", choices=["file", "directory", "batch", "agent-dirs", "formats", "validate"],
                       help="수집 명령")
    parser.add_argument("paths", nargs="*", help="파일 또는 디렉토리 경로")
    parser.add_argument("--agent-type", "-a", default="auto",
                       choices=["auto", "source_code", "binary", "parameter", "log_conf"],
                       help="대상 에이전트 타입")
    parser.add_argument("--no-recursive", action="store_true",
                       help="디렉토리 수집시 재귀 검색 비활성화")
    parser.add_argument("--documents-root", default="data/documents",
                       help="에이전트별 디렉토리 루트 경로 (기본값: data/documents)")

    args = parser.parse_args()
    cli = DocumentIngestionCLI()

    if args.command == "formats":
        cli.show_supported_formats()
        return

    if args.command == "validate":
        if not args.paths:
            print("❌ 검증할 파일 경로를 제공해주세요")
            return
        await cli.validate_ingestion(args.paths)
        return

    if args.command == "agent-dirs":
        recursive = not args.no_recursive
        success = await cli.ingest_agent_directories(args.documents_root, recursive)
        if success:
            print(f"\n🎉 에이전트별 디렉토리 수집 완료!")
            print(f"💡 서버를 재시작하여 새로운 지식을 활용하세요.")
        else:
            print(f"\n💥 에이전트별 디렉토리 수집 실패!")
            sys.exit(1)
        return

    if not args.paths:
        print("❌ 파일 또는 디렉토리 경로를 제공해주세요")
        parser.print_help()
        return

    success = False

    if args.command == "file":
        if len(args.paths) != 1:
            print("❌ 단일 파일 경로를 제공해주세요")
            return
        success = await cli.ingest_single_file(args.paths[0], args.agent_type)

    elif args.command == "directory":
        if len(args.paths) != 1:
            print("❌ 단일 디렉토리 경로를 제공해주세요")
            return
        recursive = not args.no_recursive
        success = await cli.ingest_directory(args.paths[0], args.agent_type, recursive)

    elif args.command == "batch":
        success = await cli.ingest_batch_files(args.paths, args.agent_type)

    if success:
        print(f"\n🎉 작업 완료!")
        print(f"💡 서버를 재시작하여 새로운 지식을 활용하세요.")
    else:
        print(f"\n💥 작업 실패!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())