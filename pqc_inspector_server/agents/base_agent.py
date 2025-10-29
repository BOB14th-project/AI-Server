# File: pqc_inspector_server/agents/base_agent.py
# 🤖 모든 전문 분석 에이전트들이 상속받을 추상 기본 클래스입니다.

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..services.ai_service import AIService, get_ai_service
from ..services.knowledge_manager import KnowledgeManager
from ..api.schemas import AgentAnalysisResult

class BaseAgent(ABC):
    """
    모든 에이전트의 기본이 되는 추상 클래스입니다.
    모든 에이전트는 'analyze' 메소드를 반드시 구현해야 합니다.
    """
    
    def __init__(self, model_name: str, agent_type: str):
        self.model_name = model_name
        self.agent_type = agent_type
        self.ai_service = get_ai_service()
        self.system_prompt = self._get_system_prompt()
        self.knowledge_manager: Optional[KnowledgeManager] = None

        # 에이전트별 RAG 유사도 임계값 설정
        self.rag_similarity_threshold = self._get_similarity_threshold()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        각 에이전트별 시스템 프롬프트를 반환합니다.
        """
        pass
    
    @abstractmethod
    async def analyze(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """
        파일 내용을 분석하여 결과를 딕셔너리 형태로 반환합니다.

        Args:
            file_content (bytes): 분석할 파일의 내용입니다.
            file_name (str): 분석할 파일의 이름입니다.

        Returns:
            Dict[str, Any]: AgentAnalysisResult 스키마와 호환되는 분석 결과
        """
        pass
    
    async def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """
        AI 모델을 호출하고 응답을 받습니다.
        """
        return await self.ai_service.generate_response(
            model=self.model_name,
            prompt=prompt,
            system_prompt=self.system_prompt
        )
    
    def _get_similarity_threshold(self) -> float:
        """
        에이전트별 RAG 유사도 임계값을 반환합니다.
        각 에이전트에서 override하여 최적의 임계값을 설정할 수 있습니다.
        """
        # 에이전트별 기본 임계값 (낮춰서 더 많은 컨텍스트 활용)
        thresholds = {
            "source_code": 0.05,      # 0.10 → 0.05
            "assembly_binary": 0.08,  # 0.15 → 0.08
            "logs_config": 0.10       # 0.20 → 0.10 (대폭 감소)
        }
        return thresholds.get(self.agent_type, 0.05)  # 기본값 0.05

    async def _initialize_knowledge_manager(self):
        """
        지식 매니저를 초기화합니다. (지연 초기화)
        """
        if self.knowledge_manager is None:
            from ..services.knowledge_manager import KnowledgeManagerFactory
            self.knowledge_manager = await KnowledgeManagerFactory.get_manager(self.agent_type)

    async def _get_rag_context(
        self,
        content: str,
        top_k: int = 3,
        similarity_threshold: Optional[float] = None
    ) -> str:
        """
        RAG 시스템에서 관련 컨텍스트를 검색합니다.

        Args:
            content: 검색할 쿼리 내용
            top_k: 검색할 최대 문서 수
            similarity_threshold: 유사도 임계값 (None이면 에이전트별 기본값 사용)

        Returns:
            포맷팅된 컨텍스트 문자열 (관련 컨텍스트가 없으면 빈 문자열)
        """
        try:
            await self._initialize_knowledge_manager()

            if self.knowledge_manager:
                rag_result = await self.knowledge_manager.search_relevant_context(
                    query=content,
                    top_k=top_k
                )

                contexts = rag_result.get("contexts", [])

                # 유사도 임계값 적용 (None이면 에이전트별 기본값 사용)
                threshold = similarity_threshold if similarity_threshold is not None else self.rag_similarity_threshold

                # 유사도 필터링
                filtered_contexts = [
                    ctx for ctx in contexts
                    if ctx.get('similarity', 0.0) >= threshold
                ]

                if not filtered_contexts:
                    print(f"   ℹ️ 유사도 임계값({threshold:.2f}) 이상인 컨텍스트 없음")
                    return ""

                # 필터링된 컨텍스트 수 출력
                filtered_count = len(contexts) - len(filtered_contexts)
                if filtered_count > 0:
                    print(f"   🔍 유사도 필터링: {len(contexts)}개 중 {filtered_count}개 제외됨 (임계값: {threshold:.2f})")

                # 컨텍스트를 문자열로 포맷팅
                context_text = "=== 전문가 지식 베이스 컨텍스트 ===\n"
                for i, ctx in enumerate(filtered_contexts):
                    context_text += f"\n[참조 {i+1}] {ctx['category']} ({ctx['type']})\n"
                    context_text += f"유사도: {ctx['similarity']:.3f}\n"
                    context_text += f"내용: {ctx['content']}\n"
                    context_text += f"출처: {ctx['source']}\n"
                context_text += "\n=== 컨텍스트 끝 ===\n"
                return context_text

            return ""

        except Exception as e:
            print(f"❌ RAG 컨텍스트 검색 중 오류: {e}")
            return ""

    def _parse_file_content(self, file_content: bytes) -> str:
        """
        바이트 파일 내용을 텍스트로 변환합니다.
        """
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1')
            except UnicodeDecodeError:
                return str(file_content)  # 바이너리 파일의 경우
