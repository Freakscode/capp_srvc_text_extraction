# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    s3_bucket_name: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str

    class Config:
        env_file = ".env"

settings = Settings()