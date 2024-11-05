import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuraciones de RabbitMQ
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST', '127.0.0.1')
    RABBITMQ_QUEUE: str = os.getenv('RABBITMQ_QUEUE', 'embeddings_queue')
    
    # Configuraciones de PostgreSQL
    postgres_user: str = os.getenv('postgres_user')
    postgres_password: str = os.getenv('postgres_password')
    postgres_db: str = os.getenv('postgres_db')
    postgres_host: str = os.getenv('postgres_host')
    port: str = os.getenv('port', '5432')
    
    # Configuraciones de AWS
    aws_access_key_id: str = os.getenv('aws_access_key_id')
    aws_secret_access_key: str = os.getenv('aws_secret_access_key')
    aws_region: str = os.getenv('aws_region')
    s3_bucket_name: str = os.getenv('s3_bucket_name')

    class Config:
        env_file = '.env'
        # extra = 'ignore'  # Si deseas permitir campos extra sin definir

settings = Settings()