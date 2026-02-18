# apps/rag/src/chatbot/service.py

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.rag.RAG_config import settings
from src.rag.vectorstore import VectorStore
from src.chatbot.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# 로거 설정
logger = logging.getLogger("AzanService")

class AzanChatbotService:
    def __init__(self):
        """
        챗봇 서비스 초기화
        - VectorStore 연결
        - LLM(Gemini) 설정
        - Prompt 템플릿 로드
        """
        try:
            # 1. Vector Store 연결 (apps/rag/src/rag/vectorstore.py 활용)
            self.vector_store = VectorStore()
            logger.info("[System] VectorStore connected successfully.")

            # 2. LLM 설정 (settings에서 키 가져옴)
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GENERATION_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=settings.TEMPERATURE
            )
            
            # 3. 프롬프트 템플릿 설정
            self.prompt_template = ChatPromptTemplate.from_template(USER_PROMPT_TEMPLATE)
            
            logger.info(f"[System] LLM Initialized: {settings.GENERATION_MODEL}")

        except Exception as e:
            logger.error(f"[Critical] Chatbot Service Initialization Failed: {e}")
            raise e

    def _format_to_toon(self, docs):
        """
        검색된 문서들을 LLM이 이해하기 쉬운 Table(TOON) 형식으로 변환
        """
        if not docs:
            return "관련된 공지사항 정보가 없습니다."

        # 헤더 생성
        toon_text = "| Title | Deadline | Content Summary |\n"
        toon_text += "|---|---|---|\n"

        for doc in docs:
            meta = doc.metadata
            # DB 컬럼명에 맞춰 메타데이터 추출
            title = meta.get("title", "No Title")
            deadline = meta.get("deadline_at", "N/A")
            # 본문 요약 (너무 길면 자름)
            content = doc.page_content.replace('\n', ' ')[:200]
            
            row = f"| {title} | {deadline} | {content}... |\n"
            toon_text += row
        
        return toon_text

    def get_response(self, question: str) -> str:
        """
        [Public API] 사용자의 질문을 받아 RAG 답변을 생성하여 반환
        """
        try:
            # 1. Context 추출 (Retrieval)
            logger.info(f"Querying: {question}")
            
            # vectorstore.similarity_search 사용
            retrieved_docs = self.vector_store.similarity_search(
                query=question, 
                k=settings.RETRIEVER_TOP_K
            )

            # 유사도 점수 필터링 로직이 필요하다면 vectorstore.py에 
            # similarity_search_with_score 기능을 추가해야 함.
            # 현재는 검색된 문서가 있으면 그대로 사용.
            
            if not retrieved_docs:
                logger.warning("No relevant documents found.")
                context_text = "관련된 공지사항이 없습니다. 일반적인 지식으로 답변합니다."
            else:
                context_text = self._format_to_toon(retrieved_docs)
                logger.info(f"Retrieved {len(retrieved_docs)} docs.")

            # 2. LLM 입력 데이터 구성
            input_data = {
                "system_instruction": SYSTEM_PROMPT,
                "context": context_text,
                "question": question
            }

            # 3. 답변 생성 (Generation)
            chain = self.prompt_template | self.llm | StrOutputParser()
            response = chain.invoke(input_data)
            
            return response

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "죄송합니다. 시스템 오류가 발생하여 답변을 생성할 수 없습니다."