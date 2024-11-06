# app/infraestructure/messaging/consumers/base_consumer.py
import logging
import json
from abc import ABC, abstractmethod
from app.infraestructure.messaging.rabbitmq import RabbitMQClient

class BaseConsumer(ABC):
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.rabbitmq = RabbitMQClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def process_message(self, message: dict):
        pass

    def start(self):
        self.logger.info(f"Iniciando consumidor para {self.queue_name}")
        self.rabbitmq.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._on_message
        )
        self.rabbitmq.channel.start_consuming()

    def _on_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            self.process_message(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.logger.error(f"Error procesando mensaje: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag)