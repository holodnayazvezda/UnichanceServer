from pydantic import BaseModel
from datetime import timedelta

class Settings(BaseModel):
    PROJECT_NAME: str = "Unichance API"
    DATABASE_URL: str = "sqlite:///./app_db.sqlite3"
    SECRET_KEY: str = "Unichance33"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

settings = Settings()
