# ./apps/rag/src/rag/RAG_config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 경로 설정 (root 설정)
current_file = Path(__file__).resolve()
project_root = current_file.parents[4] 
env_path = project_root / ".env"

# 2. .env 로드
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[System] Config: Loaded .env from {env_path}")
else:
    print(f"[Warning] Config: .env not found at {env_path}")
    load_dotenv()

class Config:
    PROJECT_NAME = "Azan Chatbot"

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-2.0-flash")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001") 
    TEMPERATURE = 0.3
    RETRIEVER_TOP_K = 3

    # Database
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "azan")

    # psycopg2가 사용하는 파라미터 딕셔너리 생성
    # 차후 경로 수정 시 동적 계산을 위해 property 데코레이터로 설정
    @property
    def DB_PARAMS(self):
        return {
            "dbname": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
        }

    def validate(self):
        if not self.GEMINI_API_KEY:
            raise ValueError("[ERROR] GEMINI_API_KEY가 없습니다.")

settings = Config()
settings.validate()