# app/infrastructure/aws_s3.py
import boto3
from botocore.exceptions import NoCredentialsError
from app.domain.entities.document import Document

class S3Client:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, bucket_name: str):
        """Inicializa el cliente de S3."""
        self.bucket_name = bucket_name
        try:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            print("Cliente de S3 inicializado correctamente.")
        except Exception as e:
            print(f"Error al inicializar el cliente de S3: {e}")
            raise e

    def upload_document(self, document: Document):
        """Sube un documento a S3."""
        try:
            self.s3.upload_file(document.filename, self.bucket_name, document.id)
            print(f"Documento {document.id} subido a S3 correctamente.")
        except FileNotFoundError:
            print(f"El archivo {document.filename} no fue encontrado.")
            raise
        except NoCredentialsError:
            print("Credenciales de AWS no disponibles.")
            raise
        except Exception as e:
            print(f"Error al subir el documento a S3: {e}")
            raise e