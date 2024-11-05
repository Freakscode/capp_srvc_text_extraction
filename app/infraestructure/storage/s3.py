import boto3
from botocore.exceptions import NoCredentialsError
from app.domain.entities.document import Document
import json

class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name, region_name='us-east-1'):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.bucket_name = bucket_name

    def upload_document(self, document: Document):
        try:
            document_data = json.dumps(document.to_dict())
            self.s3.put_object(Bucket=self.bucket_name, Key=document.id, Body=document_data)
            return True
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def download_document(self, document_id: str) -> Document:
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=document_id)
            document_data = json.loads(response['Body'].read().decode('utf-8'))
            document = Document(
                id=document_data['id'],
                filename=document_data['filename'],
                created_at=document_data['created_at'],
                sections=document_data['sections'],
                embeddings=document_data['embeddings'],
                metadata=document_data['metadata']
            )
            return document
        except NoCredentialsError:
            print("Credentials not available")
            return None
