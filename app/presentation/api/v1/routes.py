from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.domain.entities.document import Document
from app.domain.entities.analysis import Analysis
from app.infraestructure.database.postgres import PostgresDatabase
from app.infraestructure.storage.s3 import S3Client
from app.infraestructure.messaging.rabbitmq import RabbitMQClient
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/document")
async def upload_document(file: UploadFile = File(...)):
    try:
        document_id = str(uuid.uuid4())
        filename = file.filename
        content = await file.read()
        created_at = datetime.utcnow()

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
