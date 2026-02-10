# ./chatbot_vecDB.py

import logging
import chromadb
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from chatbot.config import CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VectorDB")

class VectorDBClient:
    _vector_store = None

    @classmethod
    def get_vector_store(cls):
        """DB 연결 객체를 생성하거나 기존 객체를 반환 (Singleton)"""
        if cls._vector_store is None:
            try:
                # 1. DB 서버 연결 (Docker)
                logger.info(f"Connecting to ChromaDB at {CONFIG.CHROMA_HOST}:{CONFIG.CHROMA_PORT}...")
                
                client = chromadb.HttpClient(
                    host=CONFIG.CHROMA_HOST, 
                    port=CONFIG.CHROMA_PORT,
                    settings=chromadb.config.Settings(
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                
                # 2. 임베딩 모델 설정
                embeddings = GoogleGenerativeAIEmbeddings(
                    model=CONFIG.EMBEDDING_MODEL,
                    google_api_key=CONFIG.GEMINI_API_KEY
                )

                # 3. LangChain 연결체 생성
                cls._vector_store = Chroma(
                    client=client,
                    collection_name=CONFIG.COLLECTION_NAME,
                    embedding_function=embeddings
                )
                logger.info(f"Successfully connected to collection: '{CONFIG.COLLECTION_NAME}'")
                
            except Exception as e:
                logger.error(f"Failed to connect to Vector DB: {str(e)}")
                cls._vector_store = None
                
        return cls._vector_store

def get_db():
    return VectorDBClient.get_vector_store()