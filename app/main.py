import uuid
import base64
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List, Dict
from fastapi.responses import HTMLResponse
from app.infraestructure.messaging.rabbitmq import RabbitMQClient
from app.core.config import get_settings

app = FastAPI()
settings = get_settings()

def create_batch(files: List[Dict]) -> List[List[Dict]]:
    """Crea batches de archivos del tamaño especificado"""
    return [files[i:i + settings.BATCH_SIZE] 
            for i in range(0, len(files), settings.BATCH_SIZE)]

@app.post("/documents")
async def upload_documents(
    files: List[UploadFile] = File(..., description="Múltiples archivos PDF")
):
    if not files:
        raise HTTPException(
            status_code=400, 
            detail="No se proporcionaron archivos"
        )
    
    try:
        rabbitmq = RabbitMQClient()
        documents = []
        
        # Procesar archivos
        for file in files:
            content = await file.read()
            document_id = str(uuid.uuid4())
            content_base64 = base64.b64encode(content).decode('utf-8')
            
            document = {
                "document_id": document_id,
                "filename": file.filename,
                "content": content_base64,
                "content_type": "application/pdf"
            }
            
            # Publicar en cola de subida
            rabbitmq.publish_upload(document)
            documents.append(document)
            await file.close()
        
        # Crear y publicar batches para procesamiento
        batches = create_batch(documents)
        for batch in batches:
            rabbitmq.publish_processing(batch)
        
        rabbitmq.close()
        
        return {
            "status": "success",
            "message": f"Se recibieron {len(files)} archivos",
            "batches": len(batches),
            "documents": [
                {"id": doc["document_id"], "filename": doc["filename"]} 
                for doc in documents
            ]
        }
        
    except Exception as e:
        logging.error(f"Error procesando archivos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar los archivos"
        )
    finally:
        for file in files:
            await file.close()