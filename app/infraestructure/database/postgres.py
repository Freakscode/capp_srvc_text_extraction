from typing import Dict, Optional
import psycopg2
import json
import uuid
from app.domain.entities.document import Document
from datetime import datetime
from app.core.config import get_settings

class PostgresDatabase:
    def __init__(self):
        settings = get_settings()
        try:
            self.connection = psycopg2.connect(
                dbname=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
                host=settings.db_host,
                port=settings.db_port
            )
            self.cursor = self.connection.cursor()
            print("Conexión a PostgreSQL establecida.")
        except Exception as e:
            print(f"Error al conectar a PostgreSQL: {e}")
            raise e
    
    def save_document_analysis(self, document_id: str, analysis_data: Dict):
        """Guarda el análisis completo del documento."""
        insert_analysis = """
        INSERT INTO document_analysis (
            document_id, 
            total_paragraphs,
            total_sentences,
            total_entities
        ) VALUES (%s, %s, %s, %s)
        """
        insert_paragraph = """
        INSERT INTO paragraphs (
            paragraph_id,
            document_id,
            text,
            position,
            style_info,
            linguistic_features
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        insert_entity = """
        INSERT INTO entities (
            document_id,
            paragraph_id,
            entity_text,
            entity_label,
            start_char,
            end_char,
            context
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute("BEGIN;")
            
            # Insertar análisis del documento
            self.cursor.execute(insert_analysis, (
                document_id,
                analysis_data.get('total_paragraphs'),
                analysis_data.get('total_sentences'),
                analysis_data.get('total_entities')
            ))
            
            # Insertar párrafos
            for paragraph_text in analysis_data.get('paragraphs', []):
                paragraph_id = str(uuid.uuid4())
                self.cursor.execute(insert_paragraph, (
                    paragraph_id,
                    document_id,
                    paragraph_text,
                    json.dumps({}),  # Asigna posición si está disponible
                    json.dumps({}),  # Asigna estilo si está disponible
                    json.dumps({})   # Asigna características lingüísticas si están disponibles
                ))
            
            # Aquí puedes insertar entidades si las tienes
            # for entity in analysis_data.get('entities', []):
            #     self.cursor.execute(insert_entity, (
            #         document_id,
            #         entity.get('paragraph_id'),
            #         entity.get('entity_text'),
            #         entity.get('entity_label'),
            #         entity.get('start_char'),
            #         entity.get('end_char'),
            #         entity.get('context')
            #     ))
            
            self.connection.commit()
            print("Análisis del documento guardado exitosamente.")
        
        except Exception as e:
            self.connection.rollback()
            print(f"Error al guardar el análisis del documento: {e}")
            raise e

    def save_document(self, document: Document):
        """Guarda un documento en la base de datos."""
        insert_doc = """
        INSERT INTO documents (id, filename, created_at, metadata)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.cursor.execute(insert_doc, (
                document.id,
                document.filename,
                document.created_at,
                json.dumps(document.metadata)
            ))
            self.connection.commit()
            print("Documento guardado exitosamente.")
        except Exception as e:
            self.connection.rollback()
            print(f"Error al guardar el documento: {e}")
            raise e

    def save_document_analysis(self, document_id: str, analysis_data: Dict):
        """Guarda el análisis completo del documento."""
        insert_analysis = """
        INSERT INTO document_analysis (
            document_id, 
            total_paragraphs,
            total_sentences,
            total_entities
        ) VALUES (%s, %s, %s, %s)
        """
        insert_paragraph = """
        INSERT INTO paragraphs (
            paragraph_id,
            document_id,
            text,
            position,
            style_info,
            linguistic_features
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        insert_entity = """
        INSERT INTO entities (
            document_id,
            paragraph_id,
            entity_text,
            entity_label,
            start_char,
            end_char,
            context
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute("BEGIN;")
            
            # Insertar análisis del documento
            self.cursor.execute(insert_analysis, (
                document_id,
                analysis_data.get('total_paragraphs'),
                analysis_data.get('total_sentences'),
                analysis_data.get('total_entities')
            ))

            # Insertar párrafos y entidades
            for paragraph in analysis_data.get('paragraphs', []):
                paragraph_id = str(uuid.uuid4())
                self.cursor.execute(insert_paragraph, (
                    paragraph_id,
                    document_id,
                    paragraph.get('text'),
                    json.dumps(paragraph.get('position')),
                    json.dumps(paragraph.get('style_info')),
                    json.dumps(paragraph.get('linguistic_features'))
                ))

                for entity in paragraph.get('entities', []):
                    self.cursor.execute(insert_entity, (
                        document_id,
                        paragraph_id,
                        entity.get('entity_text'),
                        entity.get('entity_label'),
                        entity.get('start_char'),
                        entity.get('end_char'),
                        entity.get('context')
                    ))

            self.connection.commit()
            print("Análisis del documento guardado exitosamente.")
        
        except Exception as e:
            self.connection.rollback()
            print(f"Error al guardar el análisis del documento: {e}")
            raise e

    def get_document(self, document_id: str) -> Optional[Dict]:
        """Recupera un documento de la base de datos."""
        select_doc = """
        SELECT id, filename, created_at, metadata 
        FROM documents 
        WHERE id = %s
        """
        try:
            self.cursor.execute(select_doc, (document_id,))
            doc = self.cursor.fetchone()
            if not doc:
                return None
            return {
                "id": doc[0],
                "filename": doc[1],
                "created_at": doc[2],
                "metadata": doc[3]
            }
        except Exception as e:
            print(f"Error al recuperar el documento: {e}")
            raise e

    def close(self):
        """Cierra la conexión a la base de datos."""
        try:
            self.cursor.close()
            self.connection.close()
            print("Conexión a la base de datos cerrada correctamente.")
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")