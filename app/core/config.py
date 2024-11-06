from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    
    # Colas de RabbitMQ
    UPLOAD_QUEUE: str = "document_upload_queue"
    PROCESSING_QUEUE: str = "document_processing_queue"
    ANALYSIS_QUEUE: str = "document_analysis_queue"
    
    # Límites de archivos
    MAX_FILES: int = 100
    ALLOWED_EXTENSIONS: set = {'.pdf'}
    BATCH_SIZE: int = 5

    class Config:
        env_file = ".env"
    
    # Configuración de workers
    UPLOAD_WORKERS: int = 2
    PROCESSING_WORKERS: int = 3
    
    # Timeouts y reintentos
    MESSAGE_PROCESSING_TIMEOUT: int = 300  # segundos
    MAX_RETRIES: int = 3

@lru_cache()
def get_settings():
    return Settings()