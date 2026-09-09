from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Cooking Platform 2.0"
    API_V1_STR: str = "/api/v1"
    
    MONGODB_URI: str = "mongodb://localhost:27017/ai_cooking_db"
    
    JWT_SECRET_KEY: str = "supersecretkey_change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    LLM_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
