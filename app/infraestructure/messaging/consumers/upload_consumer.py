# app/infraestructure/messaging/consumers/upload_consumer.py
from app.core.config import get_settings
from app.use_cases.extract_text import ExtractTextUseCase
from app.infraestructure.storage.s3 import S3Client
from app.domain.repositories.document_repository import DocumentRepository
from app.infraestructure.messaging.consumers.base_consumer import BaseConsumer

class UploadConsumer(BaseConsumer):
    def __init__(self):
        settings = get_settings()
        super().__init__(settings.UPLOAD_QUEUE)
        self.document_repository = DocumentRepository()
        self.s3_client = S3Client()
        
    async def process_message(self, message: dict):
        document_id = message["document_id"]
        content = message["content"]
        
        # Guardar en S3
        await self.s3_client.upload_document({
            "id": document_id,
            "content": content
        })
        
        # Actualizar estado en BD
        await self.document_repository.update_status(
            document_id, 
            "uploaded"
        )