import logging
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from numpy import mean
import time
from app.core.config import get_settings
from app.infraestructure.metrics.performance_metrics import PerformanceMetrics
from app.domain.entities.document import Document
from app.preprocessing.exceptions import PDFProcessingError
from app.domain.entities.analysis import Analysis
from app.infraestructure.database.postgres import PostgresDatabase
from app.infraestructure.storage.s3 import S3Client
from app.infraestructure.messaging.rabbitmq import RabbitMQClient
from app.preprocessing.pdf_extractor import PDFExtractor
from app.preprocessing.normalizer import TextNormalizer
from app.preprocessing.cleaner import TextCleaner
from datetime import datetime, timezone
import uuid

router = APIRouter()
metrics = PerformanceMetrics()
settings = get_settings()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    db = None
    extractor = None
    temp_pdf_path = None
    start_time = metrics.start_timer()
    
    try:
        # Generar ID y metadata inicial
        document_id = str(uuid.uuid4())
        filename = file.filename
        content = await file.read()
        file_size = len(content)
        created_at = datetime.now(timezone.utc)
        
        logging.info(f"Iniciando procesamiento del documento: {filename} (ID: {document_id})")

        # Crear instancia del documento
        document = Document(
            id=document_id,
            filename=filename,
            created_at=created_at,
            sections=[],
            embeddings=None,
            metadata={}
        )

        # Guardar archivo temporalmente
        temp_pdf_path = f"/tmp/{document_id}.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(content)
        logging.info(f"Archivo temporal guardado en: {temp_pdf_path}")

        # Inicializar DB y guardar documento
        db = PostgresDatabase()
        db.save_document(document)
        logging.info(f"Documento base guardado con ID: {document_id}")

        # Inicializar procesadores
        extractor = PDFExtractor()
        normalizer = TextNormalizer()
        cleaner = TextCleaner()

        # Extraer y procesar contenido
        extracted_data = extractor.extract_document(temp_pdf_path)
        if not isinstance(extracted_data, dict):
            logging.error("extract_document no retornó un diccionario.")
            raise PDFProcessingError("Formato de datos extraído inválido.")
        logging.info("Contenido del PDF extraído correctamente")

        # Limpiar y normalizar contenido
        cleaned_content = []
        for content_item in extracted_data.get('content', []):
            if isinstance(content_item, dict) and 'text' in content_item:
                cleaned_text = cleaner.clean(content_item['text'])
                if cleaned_text:
                    cleaned_content.append(cleaned_text)
        normalized_content = [normalizer.normalize(text) for text in cleaned_content]
        
        # Actualizar datos procesados
        extracted_data['cleaned_content'] = cleaned_content
        extracted_data['normalized_content'] = normalized_content

        # Guardar análisis y métricas
        db.save_document_analysis(document_id, extracted_data.get('statistics', {}))
        processing_time = metrics.end_timer(start_time)
        
        metrics.record_document_metrics(
            document_id=document_id,
            processing_time=processing_time,
            file_size=file_size,
            stats={
                "total_paragraphs": len(cleaned_content),
                "total_characters": sum(len(text) for text in cleaned_content),
                "document_statistics": extracted_data.get('statistics', {})
            }
        )
        
        logging.info(f"Análisis del documento guardado exitosamente. Tiempo: {processing_time:.2f}s")

        return JSONResponse(
            content={
                "document_id": document_id, 
                "status": "success",
                "metrics": metrics.get_document_metrics(document_id)
            },
            status_code=201
        )

    except Exception as e:
        logging.error(f"Error procesando el documento: {str(e)}")
        if db:
            db.connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error procesando el documento: {str(e)}")

    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
            logging.info(f"Archivo temporal eliminado: {temp_pdf_path}")
        if extractor:
            extractor.close()
        if db:
            db.close()

@router.get("/document/{document_id}")
async def get_document(document_id: str):
    try:
        db = PostgresDatabase()
        document = db.get_document(document_id)

        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        return JSONResponse(content=document.to_dict(), status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el documento")

@router.get("/analysis/{document_id}")
async def get_analysis(document_id: str):
    try:
        db = PostgresDatabase()
        analysis = db.get_document_analysis(document_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")

        return JSONResponse(content=analysis, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el análisis")

@router.get("/metrics")
async def get_processing_metrics():
    """Endpoint para obtener métricas globales de procesamiento"""
    return metrics.get_global_metrics()

@router.get("/metrics/document/{document_id}")
async def get_document_metrics(document_id: str):
    """Obtener métricas específicas de un documento"""
    doc_metrics = metrics.get_document_metrics(document_id)
    if not doc_metrics:
        raise HTTPException(status_code=404, detail="Métricas no encontradas")
    return doc_metrics

@router.post("/test_document")
async def test_process_document(file: UploadFile = File(..., description="Archivo PDF para prueba")):
    if not file:
        raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo")
    
    db = None
    extractor = None
    temp_pdf_path = None
    timer_id = "test_document_timer"
    metrics.start_timer(timer_id)
    
    try:
        # Metadata inicial
        document_id = str(uuid.uuid4())
        filename = file.filename
        content = await file.read()
        file_size = len(content)
        created_at = datetime.now(timezone.utc)
        temp_pdf_path = f"/tmp/{document_id}.pdf"
        
        logging.info(f"Iniciando prueba de procesamiento: {filename}")
        # Guardar archivo temporal
        with open(temp_pdf_path, "wb") as f:
            f.write(content)
        logging.info(f"Archivo temporal guardado: {temp_pdf_path}")
        # Crear documento base
        document = Document(
            id=document_id,
            filename=filename,
            created_at=created_at,
            sections=[],
            embeddings=None,
            metadata={}
        )
        # Inicializar DB y guardar documento
        db = PostgresDatabase()
        db.save_document(document)
        
        # Inicializar procesadores
        extractor = PDFExtractor()
        normalizer = TextNormalizer()
        cleaner = TextCleaner()
        # Procesar documento
        extracted_data = extractor.extract_document(temp_pdf_path)
        cleaned_content = []
        for content_item in extracted_data.get('content', []):
            if isinstance(content_item, dict) and 'text' in content_item:
                cleaned_text = cleaner.clean(content_item['text'])
                if cleaned_text:
                    cleaned_content.append(cleaned_text)
        normalized_content = [normalizer.normalize(text) for text in cleaned_content]
        
        # Asignar párrafos limpiados
        extracted_data['paragraphs'] = cleaned_content
        extracted_data['normalized_paragraphs'] = normalized_content

        # Opcional: Loguear el texto completo extraído
        logging.info(f"Texto completo extraído: {extracted_data.get('full_text', '')}")
    
        # Guardar análisis y métricas
        db.save_document_analysis(document_id, extracted_data)
        processing_time = metrics.end_timer(timer_id)
        
        metrics.record_document_metrics(
            document_id=document_id,
            processing_time=processing_time,
            file_size=file_size,
            stats={
                "total_paragraphs": len(cleaned_content),
                "total_characters": sum(len(text) for text in cleaned_content),
                "document_statistics": extracted_data.get('statistics', {})
            }
        )
        
        logging.info(f"Análisis guardado exitosamente. Tiempo: {processing_time:.2f}s")
        return JSONResponse(
            content={
                "document_id": document_id, 
                "status": "success",
                "metrics": metrics.get_document_metrics(document_id),
                "extracted_data": extracted_data
            },
            status_code=201
        )
    except PDFProcessingError as e:
        logging.error(f"Error en prueba de procesamiento: {str(e)}")
        if db:
            db.connection.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error en prueba de procesamiento: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Error en prueba de procesamiento: {str(e)}")
        if db:
            db.connection.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error en prueba de procesamiento: {str(e)}"
        )
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
            logging.info(f"Archivo temporal eliminado: {temp_pdf_path}")
        if extractor:
            extractor.close()
        if db:
            db.close()