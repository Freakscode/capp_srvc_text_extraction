from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field, ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Configuración de PostgreSQL
    db_name: str = Field(env="DB_NAME")
    db_user: str = Field(env="DB_USER")
    db_password: str = Field(env="DB_PASSWORD")
    db_host: str = Field(env="DB_HOST")
    db_port: int = Field(env="DB_PORT")
    
    # Configuración de AWS S3
    aws_access_key_id: str = Field(env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(env="AWS_SECRET_ACCESS_KEY")
    aws_bucket_name: str = Field(env="AWS_BUCKET_NAME")
    
    # Configuración de RabbitMQ
    RABBITMQ_HOST: str = Field(default="localhost", env="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(default=5672, env="RABBITMQ_PORT")
    RABBITMQ_USER: str = Field(default="guest", env="RABBITMQ_USER")
    RABBITMQ_PASS: str = Field(default="guest", env="RABBITMQ_PASS")
    
    # Colas de RabbitMQ
    UPLOAD_QUEUE: str = Field(default="document_upload_queue", env="UPLOAD_QUEUE")
    PROCESSING_QUEUE: str = Field(default="document_processing_queue", env="PROCESSING_QUEUE")
    ANALYSIS_QUEUE: str = Field(default="document_analysis_queue", env="ANALYSIS_QUEUE")
    
    # Límites de archivos
    MAX_FILES: int = Field(default=100, env="MAX_FILES")
    ALLOWED_EXTENSIONS: set = {'.pdf'}
    BATCH_SIZE: int = Field(default=5, env="BATCH_SIZE")
    
    # Configuración de AWS S3
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_bucket_name: Optional[str] = Field(default=None, env="AWS_BUCKET_NAME")
    
    # Configuración de workers
    UPLOAD_WORKERS: int = Field(default=2, env="UPLOAD_WORKERS")
    PROCESSING_WORKERS: int = Field(default=3, env="PROCESSING_WORKERS")
    
    # Timeouts y reintentos
    MESSAGE_PROCESSING_TIMEOUT: int = Field(default=300, env="MESSAGE_PROCESSING_TIMEOUT")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

@lru_cache()
def get_settings():
    return Settings()