# ./chatbot_service.py

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chatbot.config import CONFIG
from vectorDB.client import get_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ChatbotService")

class ChatbotByGemini:
    def __init__(self):
        # 1. DB 연결 (Singleton 활용)
        self.vector_store = get_db()
        
        # 2. LLM 설정
        self.llm = ChatGoogleGenerativeAI(
            model=CONFIG.GENERATION_MODEL,
            google_api_key=CONFIG.GEMINI_API_KEY,
            temperature=CONFIG.TEMPERATURE
        )
        logger.info(f"Initialized LLM with model: {CONFIG.GENERATION_MODEL}")
        
        # 3. 프롬프트 템플릿 (시스템 프롬프트 + TOON 포맷 적용)
        self.prompt_template = ChatPromptTemplate.from_template("""
        {system_instruction}
        
        [참고 자료 (TOON Format)]
        {context}
        
        [사용자 질문]
        {question}
        
        위 참고 자료를 바탕으로 답변해주세요.
        """)

    def _format_to_toon(self, docs):
        """검색된 문서들을 TOON(표) 형식으로 변환"""
        if not docs:
            return "관련된 공지사항 정보가 없습니다."

        toon_text = "|ID|Category|Deadline|Content Summary|\n"
        toon_text += "|---|---|---|---|\n"

        for doc in docs:
            meta = doc.metadata
            content = doc.page_content.replace('\n', ' ')[:200]
            row = f"|{meta.get('notice_id')}|{meta.get('category')}|{meta.get('deadline')}|{content}...|\n"
            toon_text += row
        
        return toon_text

    def extract_context(self, query: str):
        """
        사용자 질문을 받아 DB에서 유사한 문서를 검색하고 TOON 포맷으로 반환
        """
        if not self.vector_store:
            logger.error("Vector DB is not connected.")
            return "DB 연결 실패"

        try:
            # 1. 유사도 검색 (Threshold 필터링)
            results = self.vector_store.similarity_search_with_relevance_scores(query, k=3)
            score_lst = [score for _, score in results]
            filtered_docs = [doc for doc, score in results if score >= CONFIG.SIMILARITY_THRESHOLD]
            
            # 2. 결과가 없으면 로그 남기고 반환
            if not filtered_docs:
                logger.warning(f"No relevant documents found above threshold {CONFIG.SIMILARITY_THRESHOLD} > {max(score_lst)}")
                return "검색 결과가 없습니다 (유사도 낮음)."
            
            logger.info(f"Found {len(filtered_docs)} relevant documents. score : {max(score_lst)}")
            
            # 3. TOON 포맷 변환
            return self._format_to_toon(filtered_docs)
            
        except Exception as e:
            logger.error(f"Error during context extraction: {str(e)}")
            return "검색 오류 발생"

    def answer(self, query: str, context: str):
        """
        질문과 컨텍스트를 받아 LLM 답변 생성
        """
        input_data = {
            "system_instruction": CONFIG.PROMPT,
            "context": context,
            "question": query
        }
        
        chain = self.prompt_template | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke(input_data)
            return response
        except Exception as e:
            logger.error(f"Answer generation failed: {str(e)}")
            return f"답변 생성 실패: {str(e)}"