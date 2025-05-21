from typing import List
from asyncpg import create_pool
from src.core.config import settings

class VectorDB:
    _pool = None

    @classmethod
    async def get_pool(cls):
        if not cls._pool:
            print(f"Connecting to DB at: {settings.DB_HOST}")
            try:
                cls._pool = await create_pool(
                    dsn=f"postgres://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
                    min_size=5,
                    max_size=20,
                    max_inactive_connection_lifetime=300
                )
                await cls.setup_database()  
            except Exception as e:
                raise e
            
    @classmethod
    async def close_pool(cls):
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None

    @classmethod
    async def setup_database(cls):
        async with cls._pool.acquire() as conn:
            
            await conn.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS company_data (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector(384)
                );
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS company_data_hnsw_idx
                ON company_data
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
    
    @classmethod
    async def search(cls, embedding: List[float], limit: int = 3):
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(
                """SELECT content, 1 - (embedding <=> $1) as score
                   FROM company_data
                   WHERE 1 - (embedding <=> $1) > 0.7
                   ORDER BY score DESC
                   LIMIT $2
                   USING INDEX hnsw_index""",
                embedding, limit
            )