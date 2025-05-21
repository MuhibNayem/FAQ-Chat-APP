from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str 
    DB_USER: str 
    DB_PASS: str
    DB_PORT: int
    DB_NAME: str
    BEDROCK_REGION: str
    CACHE_TTL: int 
    RATE_LIMIT: str 
    MODEL_BATCH_SIZE: int
    API_KEY: str
    USE_GPU: bool = False
    MODEL_ID: str
    
    class Config:
        env_file = ".env"

settings = Settings()