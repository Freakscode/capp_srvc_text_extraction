# app/services/document_processing_service.py

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from sentence_transformers import SentenceTransformer
import psycopg2
from app.core.config import settings
from app.services.nlp_service import NLPService
import logging

logger = logging.getLogger(__name__)

# Inicializar el modelo de Sentence BERT
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
nlp_service = NLPService()

def list_pdf_files() -> list:
    s3_client = boto3.client('s3', region_name=settings.aws_region)
    pdf_files = []
    try:
        response = s3_client.list_objects_v2(Bucket=settings.s3_bucket_name)
        for obj in response.get('Contents', []):
            if obj['Key'].lower().endswith('.pdf'):
                pdf_files.append(obj['Key'])
    except (NoCredentialsError, PartialCredentialsError):
        logger.error("Credenciales de AWS no configuradas correctamente.")
    except Exception as e:
        logger.error(f"Error al listar los archivos: {e}")
    return pdf_files

def download_pdf(s3_client, key: str) -> bytes:
    try:
        response = s3_client.get_object(Bucket=settings.s3_bucket_name, Key=key)
        pdf_content = response['Body'].read()
        return pdf_content
    except Exception as e:
        logger.error(f"Error al descargar {key}: {e}")
        return None

def save_embedding_to_db(document_name: str, embedding: list):
    conn = psycopg2.connect(
        host=settings.postgres_host,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password
    )
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO document_embeddings (document_name, embedding)
    VALUES (%s, %s);
    """
    cursor.execute(insert_query, (document_name, embedding))
    conn.commit()
    cursor.close()
    conn.close()

def process_s3_pdfs():
    s3_client = boto3.client('s3', region_name=settings.aws_region)
    pdf_files = list_pdf_files()
    for pdf_file in pdf_files:
        logger.info(f"Procesando {pdf_file}...")
        pdf_content = download_pdf(s3_client, pdf_file)
        if pdf_content:
            result = nlp_service.process_document(pdf_content)
            text = result["text"]
            analysis = result["analysis"]
            embedding = model.encode(text).tolist()
            save_embedding_to_db(pdf_file, embedding)
            logger.info(f"{pdf_file} procesado y guardado correctamente.")
        else:
            logger.error(f"No se pudo descargar {pdf_file}.")