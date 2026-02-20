# apps/rag/src/chatbot/service.py

import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory

from src.rag.RAG_config import settings
from src.rag.vectorstore import VectorStore
from src.chatbot.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, CONDENSE_QUESTION_PROMPT

logger = logging.getLogger("AzanService")

class AzanChatbotService:
    def __init__(self):
        """챗봇 서비스 초기화 (VectorStore, LLM, Memory 설정)"""
        try:
            self.vector_store = VectorStore()
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GENERATION_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=settings.TEMPERATURE
            )
            
            # 최신 표준(langchain_core) 메모리 사용
            self.memory = InMemoryChatMessageHistory()
            
            self.condense_prompt = ChatPromptTemplate.from_template(CONDENSE_QUESTION_PROMPT)
            self.answer_prompt = ChatPromptTemplate.from_template(USER_PROMPT_TEMPLATE)
            
            logger.info("[System] Azan Service with Modern Memory Initialized.")

        except Exception as e:
            logger.error(f"Initialization Failed: {e}")
            raise e

    def _format_to_toon(self, docs):
        """
        검색된 문서들을 LLM이 이해하기 쉬운 Table(TOON) 형식으로 변환
        """
        if not docs:
            return "관련된 공지사항 정보가 없습니다."

        toon_text = "| Title | Deadline | Content Summary |\n"
        toon_text += "|---|---|---|\n"

        for doc in docs:
            meta = doc.metadata
            title = meta.get("title", "No Title")
            deadline = meta.get("deadline_at", "N/A")
            content = doc.page_content.replace('\n', ' ')[:200]
            
            row = f"| {title} | {deadline} | {content}... |\n"
            toon_text += row
        
        return toon_text

    def get_response(self, question: str) -> str:
        try:
            # 1. 대화 기록 추출
            messages = self.memory.messages
            chat_history = "\n".join(
                [f"{'User' if msg.type == 'human' else 'Azan'}: {msg.content}" for msg in messages]
            )

            # 2. 질문 재구성 (Condense Question)
            if chat_history:
                condense_chain = self.condense_prompt | self.llm | StrOutputParser()
                standalone_question = condense_chain.invoke({
                    "chat_history": chat_history,
                    "question": question
                })
                logger.info(f"Standalone Question: {standalone_question}")
                
                # 밀리초 단위 호출 시 트래픽이 터짐 (500 Error)
                time.sleep(1.5) 
                
            else:
                standalone_question = question

            # 3. DB 검색 (Retrieval)
            retrieved_docs = self.vector_store.similarity_search(standalone_question, k=settings.RETRIEVER_TOP_K)
            context_text = self._format_to_toon(retrieved_docs) if retrieved_docs else "정보 없음"

            # 4. 최종 답변 생성 (Generation)
            answer_chain = self.answer_prompt | self.llm | StrOutputParser()
            response = answer_chain.invoke({
                "system_instruction": SYSTEM_PROMPT,
                "chat_history": chat_history,
                "context": context_text,
                "question": question
            })

            # 5. 메모리에 현재 대화 저장
            self.memory.add_user_message(question)
            self.memory.add_ai_message(response)
            
            return response

        except Exception as e:
            logger.error(f"Error: {e}")
            return "오류가 발생했습니다."