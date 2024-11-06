# app/infraestructure/messaging/consumers/processing_consumer.py
from app.use_cases.process_document import ProcessDocumentUseCase
from app.core.config import get_settings
import uuid
from app.infraestructure.messaging.consumers.base_consumer import BaseConsumer
from app.infraestructure.metrics.performance_metrics import PerformanceMetrics

class ProcessingConsumer(BaseConsumer):
    def __init__(self):
        settings = get_settings()
        super().__init__(settings.PROCESSING_QUEUE)
        self.process_document = ProcessDocumentUseCase()
        self.metrics = PerformanceMetrics()
        
    @PerformanceMetrics().measure_time("batch")
    async def process_message(self, message: dict):
        batch = message["batch"]
        batch_id = str(uuid.uuid4())
        
        for document in batch:
            await self.process_document_with_metrics(document, batch_id)
    
    @PerformanceMetrics().measure_time("document")
    async def process_document_with_metrics(self, document: dict, batch_id: str):
        try:
            analysis = await self.process_document.execute(document)
            
            self.rabbitmq.publish_analysis({
                "document_id": document["document_id"],
                "batch_id": batch_id,
                "analysis": analysis.to_dict(),
                "processing_metrics": self.metrics.get_metrics()
            })
        except Exception as e:
            self.logger.error(f"Error procesando documento {document['document_id']}: {str(e)}")
            raise