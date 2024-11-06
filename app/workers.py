# app/workers.py
import asyncio
import multiprocessing
from app.infraestructure.messaging.consumers.upload_consumer import UploadConsumer
from app.infraestructure.messaging.consumers.processing_consumer import ProcessingConsumer
from app.core.config import get_settings

settings = get_settings()

def run_consumer(consumer_class):
    consumer = consumer_class()
    consumer.start()

def main():
    processes = []
    consumers = [UploadConsumer, ProcessingConsumer]
    
    for consumer_class in consumers:
        process = multiprocessing.Process(
            target=run_consumer,
            args=(consumer_class,)
        )
        processes.append(process)
        process.start()

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            process.terminate()

if __name__ == "__main__":
    main()