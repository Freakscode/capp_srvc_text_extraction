# app/use_cases/process_document.py
from ..domain.entities.document import Document
from ..preprocessing.cleaner import TextCleaner
from ..semantic.embedding import EmbeddingGenerator

class ProcessDocumentUseCase:
    def __init__(
        self, 
        cleaner: TextCleaner,
        embedding_generator: EmbeddingGenerator
    ):
        self.cleaner = cleaner
        self.embedding_generator = embedding_generator

    async def execute(self, document: Document) -> dict:
        cleaned_text = self.cleaner.clean(document.content)
        embeddings = self.embedding_generator.generate(cleaned_text)
        return {
            "document_id": document.id,
            "embeddings": embeddings,
            "metadata": document.metadata
        }