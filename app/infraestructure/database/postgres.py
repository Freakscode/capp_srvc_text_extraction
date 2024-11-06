from typing import Dict
import psycopg2
import json
import uuid
from app.domain.entities.document import Document
from app.domain.entities.document import DocumentSection, SyntaxNode
from datetime import datetime

# app/infraestructure/database/postgres.py
class PostgresDatabase:
    def save_document_analysis(self, document_id: str, analysis_data: Dict):
        """Guarda el análisis completo del documento"""
        # Insertar información básica del documento
        insert_doc = """
        INSERT INTO document_analysis (
            document_id, 
            created_at,
            total_paragraphs,
            total_sentences,
            total_entities
        ) VALUES (%s, NOW(), %s, %s, %s)
        """
        
        # Insertar párrafos
        insert_paragraph = """
        INSERT INTO paragraphs (
            document_id,
            paragraph_id,
            text,
            position,
            style_info,
            linguistic_features
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Insertar entidades
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
            # Comenzar transacción
            self.cursor.execute("BEGIN")
            
            # Insertar documento
            self.cursor.execute(insert_doc, (
                document_id,
                len(analysis_data['paragraphs']),
                sum(len(p['sentences']) for p in analysis_data['paragraphs']),
                sum(len(p['entities']) for p in analysis_data['paragraphs'])
            ))
            
            # Insertar párrafos y entidades
            for paragraph in analysis_data['paragraphs']:
                paragraph_id = str(uuid.uuid4())
                
                self.cursor.execute(insert_paragraph, (
                    document_id,
                    paragraph_id,
                    paragraph['original']['text'],
                    json.dumps(paragraph['original']['position']),
                    json.dumps(paragraph['original']['style']),
                    json.dumps(paragraph['linguistic_features'])
                ))
                
                for entity in paragraph['entities']:
                    self.cursor.execute(insert_entity, (
                        document_id,
                        paragraph_id,
                        entity['text'],
                        entity['label'],
                        entity['start_char'],
                        entity['end_char'],
                        entity['context']
                    ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error saving document analysis: {e}")
            return False