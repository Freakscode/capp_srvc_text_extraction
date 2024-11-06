import pika
import json
from typing import Any, Dict, List
from app.core.config import get_settings

settings = get_settings()

class RabbitMQClient:
    def __init__(self):
        self.credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER, 
            settings.RABBITMQ_PASS
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=self.credentials
            )
        )
        self.channel = self.connection.channel()
        
        # Declarar todas las colas
        self.channel.queue_declare(queue=settings.UPLOAD_QUEUE)
        self.channel.queue_declare(queue=settings.PROCESSING_QUEUE)
        self.channel.queue_declare(queue=settings.ANALYSIS_QUEUE)

    def publish_upload(self, document: Dict[str, Any]):
        """Publica documento en cola de subida"""
        self.channel.basic_publish(
            exchange='',
            routing_key=settings.UPLOAD_QUEUE,
            body=json.dumps(document)
        )

    def publish_processing(self, batch: List[Dict[str, Any]]):
        """Publica batch en cola de procesamiento"""
        self.channel.basic_publish(
            exchange='',
            routing_key=settings.PROCESSING_QUEUE,
            body=json.dumps({"batch": batch})
        )

    def publish_analysis(self, document: Dict[str, Any]):
        """Publica documento en cola de análisis"""
        self.channel.basic_publish(
            exchange='',
            routing_key=settings.ANALYSIS_QUEUE,
            body=json.dumps(document)
        )

    def close(self):
        if not self.connection.is_closed:
            self.connection.close()