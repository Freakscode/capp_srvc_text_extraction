import psycopg2
from app.domain.entities.document import Document
from app.domain.entities.document import DocumentSection, SyntaxNode
from datetime import datetime

class PostgresDatabase:
    def __init__(self, db_name, user, password, host, port):
        self.connection = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()

    def save_document(self, document: Document):
        insert_document_query = """
        INSERT INTO documents (id, filename, created_at, embeddings, metadata)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_document_query, (
            document.id,
            document.filename,
            document.created_at,
            document.embeddings,
            document.metadata
        ))

        for section in document.sections:
            insert_section_query = """
            INSERT INTO document_sections (document_id, content, position, metadata)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(insert_section_query, (
                document.id,
                section.content,
                section.position,
                section.metadata
            ))

            for node in section.syntax_tree:
                insert_node_query = """
                INSERT INTO syntax_nodes (section_id, text, start_pos, end_pos, type, syntactic_info, confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(insert_node_query, (
                    section.id,
                    node.text,
                    node.start_pos,
                    node.end_pos,
                    node.type,
                    node.syntactic_info,
                    node.confidence
                ))

        self.connection.commit()

    def get_document(self, document_id: str) -> Document:
        select_document_query = """
        SELECT id, filename, created_at, embeddings, metadata
        FROM documents
        WHERE id = %s
        """
        self.cursor.execute(select_document_query, (document_id,))
        document_row = self.cursor.fetchone()

        select_sections_query = """
        SELECT id, content, position, metadata
        FROM document_sections
        WHERE document_id = %s
        """
        self.cursor.execute(select_sections_query, (document_id,))
        sections_rows = self.cursor.fetchall()

        sections = []
        for section_row in sections_rows:
            select_nodes_query = """
            SELECT text, start_pos, end_pos, type, syntactic_info, confidence
            FROM syntax_nodes
            WHERE section_id = %s
            """
            self.cursor.execute(select_nodes_query, (section_row[0],))
            nodes_rows = self.cursor.fetchall()

            nodes = [
                SyntaxNode(
                    text=row[0],
                    start_pos=row[1],
                    end_pos=row[2],
                    type=row[3],
                    syntactic_info=row[4],
                    confidence=row[5]
                )
                for row in nodes_rows
            ]

            sections.append(
                DocumentSection(
                    content=section_row[1],
                    position=section_row[2],
                    syntax_tree=nodes,
                    metadata=section_row[3]
                )
            )

        document = Document(
            id=document_row[0],
            filename=document_row[1],
            created_at=document_row[2],
            sections=sections,
            embeddings=document_row[3],
            metadata=document_row[4]
        )

        return document
