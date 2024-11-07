import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from numpy import mean
from app.infraestructure.metrics.performance_metrics import PerformanceMetrics
from app.domain.entities.document import Document
from app.domain.entities.analysis import Analysis
from app.infraestructure.database.postgres import PostgresDatabase
from app.infraestructure.storage.s3 import S3Client
from app.infraestructure.messaging.rabbitmq import RabbitMQClient
from app.preprocessing.pdf_extractor import PDFExtractor
from app.preprocessing.normalizer import TextNormalizer
from app.preprocessing.cleaner import TextCleaner
from datetime import datetime
import uuid
import os

router = APIRouter()
metrics = PerformanceMetrics()

@router.post("/document")
async def upload_document(file: UploadFile = File(...)):
    try:
        document_id = str(uuid.uuid4())
        filename = file.filename
        content = await file.read()
        created_at = datetime.now(datetime.timezone.utc)

        document = Document(
            id=document_id,
            filename=filename,
            created_at=created_at,
            sections=[],  # Secciones vacías por ahora
            embeddings=None,
            metadata={}
        )

        # Guardar el documento en la base de datos
        db = PostgresDatabase(db_name="your_db", user="your_user", password="your_password", host="your_host", port="your_port")
        db.save_document(document)

        # Subir el documento a S3
        s3 = S3Client(aws_access_key_id="your_access_key", aws_secret_access_key="your_secret_key", bucket_name="your_bucket")
        s3.upload_document(document)

        return JSONResponse(content={"document_id": document_id}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al cargar el documento")

@router.get("/document/{document_id}")
async def get_document(document_id: str):
    try:
        # Recuperar el documento de la base de datos
        db = PostgresDatabase(db_name="your_db", user="your_user", password="your_password", host="your_host", port="your_port")
        document = db.get_document(document_id)

        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        return JSONResponse(content=document.to_dict(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el documento")

@router.get("/analysis/{document_id}")
async def get_analysis(document_id: str):
    try:
        # Recuperar el análisis de RabbitMQ
        rabbitmq = RabbitMQClient(host="your_rabbitmq_host", queue="your_queue")
        analysis = rabbitmq.consume_analysis(lambda x: x)

        if not analysis:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")

        return JSONResponse(content=analysis.to_dict(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el análisis")

@router.get("/metrics")
async def get_processing_metrics():
    """Endpoint para obtener métricas de procesamiento"""
    return metrics.get_metrics()

@router.get("/metrics/document/{document_id}")
async def get_document_metrics(document_id: str):
    """Obtener métricas específicas de un documento"""
    doc_time = metrics.document_times.get(document_id)
    if not doc_time:
        raise HTTPException(status_code=404, detail="Métricas no encontradas")
    
    return {
        "document_id": document_id,
        "processing_time": doc_time,
        "comparison": {
            "vs_average": doc_time - mean(metrics.document_times.values()),
            "percentile": len([t for t in metrics.document_times.values() if t <= doc_time]) / len(metrics.document_times) * 100
        }
    }

@router.post("/test_document", summary="Procesar un solo documento PDF para probar el flujo completo")
async def test_process_document(file: UploadFile = File(..., description="Archivo PDF para prueba")):
    if not file:
        raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo")
    
    document_id = str(uuid.uuid4())
    temp_pdf_path = f"/tmp/{document_id}.pdf"
    
    try:
        # Guardar el archivo temporalmente
        with open(temp_pdf_path, "wb") as f:
            f.write(await file.read())
        
        # Inicializar procesadores
        extractor = PDFExtractor()
        normalizer = TextNormalizer()
        cleaner = TextCleaner()
        db = PostgresDatabase()
        
        # Extraer contenido del PDF
        extracted_data = extractor.extract_document(temp_pdf_path)
        
        # Procesar texto
        cleaned_content = [cleaner.clean(text) for text in extracted_data.get('content', [])]
        normalized_content = [normalizer.normalize(text) for text in cleaned_content]
        
        # Actualizar datos extraídos con texto limpio y normalizado
        extracted_data['cleaned_content'] = cleaned_content
        extracted_data['normalized_content'] = normalized_content
        
        # Guardar análisis en la base de datos
        db.save_document_analysis(document_id, extracted_data)
        
        return JSONResponse(content={
            "document_id": document_id,
            "extracted_data": extracted_data
        })
    
    except Exception as e:
        logging.error(f"Error procesando el documento: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el documento")
    
    finally:
        # Limpiar recursos
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        extractor.close()