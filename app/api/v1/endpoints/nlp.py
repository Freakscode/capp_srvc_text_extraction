from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.nlp_model import NLPBatchResponse
import uuid
import logging
from app.services.nlp_service import NLPService
import pika
import json
import os
from concurrent.futures import ProcessPoolExecutor

router = APIRouter()

# Configuración de RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'embeddings_queue')

# Definir la función de procesamiento a nivel de módulo
def process_file(content, filename, doc_id):
    service = NLPService()
    result = service.process_document(content, filename)
    return {
        "document_id": doc_id,
        "filename": result["filename"],
        "entities": result["analysis"]["entities"],
        "tokens": result["analysis"]["tokens"]
    }

@router.post("/extract-text", response_model=NLPBatchResponse)
async def extract_text(files: List[UploadFile] = File(...)):
    try:
        # Validar archivos
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
        
        # Leer los contenidos de los archivos de manera asíncrona
        contents = [await file.read() for file in files]
        filenames = [file.filename for file in files]
        document_ids = [str(uuid.uuid4()) for _ in files]
        
        # Combinar los datos en una lista de tuplas
        documentos = list(zip(contents, filenames, document_ids))
        
        # Dividir los documentos en lotes de 5
        lotes = list(dividir_en_lotes(documentos, 5))
        
        # Conectar a RabbitMQ una vez
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        
        nlp_documents = []
        
        # Procesar cada lote
        for lote in lotes:
            lote_contents, lote_filenames, lote_document_ids = zip(*lote)
            
            # Utilizar ProcessPoolExecutor para procesar en paralelo
            with ProcessPoolExecutor() as executor:
                results = list(executor.map(process_file, lote_contents, lote_filenames, lote_document_ids))
            
            # Publicar cada resultado en la cola
            for result in results:
                tokens = result["tokens"]
                document_id = result["document_id"]
                filename = result["filename"]
                message = {
                    'tokens': tokens,
                    'document_id': document_id,
                    'filename': filename
                }
                channel.basic_publish(
                    exchange='',
                    routing_key=RABBITMQ_QUEUE,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Hacer que el mensaje sea persistente
                    )
                )
                nlp_documents.append({
                    'document_id': document_id,
                    'entities': result["entities"],
                    'tokens': tokens,
                    'filename': filename
                })
        
        # Cerrar la conexión de RabbitMQ
        connection.close()
        
        # Preparar la respuesta para el cliente
        return NLPBatchResponse(documents=nlp_documents)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error en /extract-text: {e}")
        raise HTTPException(status_code=500, detail="Error procesando los documentos.")
    

def dividir_en_lotes(lista, tamaño_lote):
    """Divide una lista en sublistas de tamaño determinado."""
    for i in range(0, len(lista), tamaño_lote):
        yield lista[i:i + tamaño_lote]