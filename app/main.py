import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
# from app.api.v1.endpoints import nlp  # Eliminado

from app.domain.entities.document import Document
from app.domain.entities.analysis import Analysis
from app.domain.repositories.document_repository import DocumentRepository
from app.domain.value_objects.nlp_result import NLPResult
from app.infraestructure.database.postgres import PostgresDatabase
from app.infraestructure.messaging.rabbitmq import RabbitMQClient
from app.infraestructure.storage.s3 import S3Client
from app.use_cases.extract_text import ExtractTextUseCase
from app.use_cases.process_document import ProcessDocumentUseCase
from datetime import datetime
import uuid

app = FastAPI()

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Incluir el router de NLP - Eliminado
# app.include_router(nlp.router, prefix="/api/v1/nlp")

@app.get("/")
def read_root():
    return {"message": "Microservicio NLP funcionando correctamente"}

# Endpoint para manejar la carga de documentos
@app.post("/document")
async def upload_document(file: UploadFile = File(...)):
    ...

# Endpoint para manejar la recuperación de documentos
@app.get("/document/{document_id}")
async def get_document(document_id: str):
    ...

# Endpoint para manejar la recuperación de análisis
@app.get("/analysis/{document_id}")
async def get_analysis(document_id: str):
    ...