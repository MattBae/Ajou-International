# apps/rag/init_db.py

import psycopg2
from src.rag.RAG_config import settings

def init_db():
    try:
        print(f"[Info] Connecting to database: {settings.POSTGRES_DB}")
        
        # 새로운 설정(azan DB)으로 접속
        conn = psycopg2.connect(**settings.DB_PARAMS)
        conn.autocommit = True
        cur = conn.cursor()

        print("[Info] pgvector 확장 기능을 활성화합니다...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        print("[Info] notices 테이블을 생성합니다...")
        # Gemini 임베딩 모델 차원: 3072
        create_table_query = """
        CREATE TABLE IF NOT EXISTS notices (
            id SERIAL PRIMARY KEY,
            source_type VARCHAR(50),
            source_name VARCHAR(100),
            source_url TEXT,
            title TEXT NOT NULL,
            body TEXT,
            dedupe_hash VARCHAR(64) UNIQUE,
            embedding vector(3072), 
            is_embedded BOOLEAN DEFAULT FALSE,
            is_processed BOOLEAN DEFAULT FALSE,
            published_at TIMESTAMP,
            deadline_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        cur.execute(create_table_query)
        
        # 인덱스 생성 (선택 사항, 에러나면 무시해도 됨)
        try:
            index_query = """
            CREATE INDEX IF NOT EXISTS notices_embedding_idx 
            ON notices USING hnsw (embedding vector_cosine_ops);
            """
            cur.execute(index_query)
        except Exception as e:
            print(f"[Warning] 인덱스 생성 중 경고 (무시 가능): {e}")

        print(f"[Success] '{settings.POSTGRES_DB}' 데이터베이스 초기화 완료!")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"[Error] DB 초기화 실패: {e}")

if __name__ == "__main__":
    init_db()