from app.domain.entities.document import Document

class DocumentRepository:
    def save_document(self, document: Document):
        # Implementar lógica para guardar el documento en la base de datos
        pass

    def get_document(self, document_id: str) -> Document:
        # Implementar lógica para recuperar el documento de la base de datos
        pass
