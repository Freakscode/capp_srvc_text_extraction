import pika
import json
from app.domain.entities.analysis import Analysis

class RabbitMQClient:
    def __init__(self, host: str, queue: str):
        self.host = host
        self.queue = queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def publish_analysis(self, analysis: Analysis):
        message = json.dumps(analysis.to_dict())
        self.channel.basic_publish(exchange='', routing_key=self.queue, body=message)

    def consume_analysis(self, callback):
        def on_message(channel, method, properties, body):
            analysis_data = json.loads(body)
            analysis = Analysis(
                document_id=analysis_data['document_id'],
                syntax_nodes=analysis_data['syntax_nodes'],
                embeddings=analysis_data['embeddings'],
                metadata=analysis_data['metadata']
            )
            callback(analysis)

        self.channel.basic_consume(queue=self.queue, on_message_callback=on_message, auto_ack=True)
        self.channel.start_consuming()
