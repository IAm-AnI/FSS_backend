from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FRONTEND_ORIGIN: str
    SESSION_SECRET: str = "fallback-secret"
    ENV: str = "development"
    ENV_PORT: int = 10000
    DATABASE_URL: str
    SESSION_SECRET: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()