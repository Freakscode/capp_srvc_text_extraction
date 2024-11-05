# app/use_cases/process_document.py
from ..domain.entities.document import Document
from ..domain.entities.analysis import Analysis
from ..preprocessing.cleaner import TextCleaner
from ..semantic.embedding import EmbeddingGenerator
from ..semantic.entity_extractor import EntityExtractor
from ..semantic.summarizing import TextSummarizer

class ProcessDocumentUseCase:
    def __init__(
        self, 
        cleaner: TextCleaner,
        embedding_generator: EmbeddingGenerator,
        entity_extractor: EntityExtractor,
        summarizer: TextSummarizer
    ):
        self.cleaner = cleaner
        self.embedding_generator = embedding_generator
        self.entity_extractor = entity_extractor
        self.summarizer = summarizer

    async def execute(self, document: Document) -> Analysis:
        cleaned_text = self.cleaner.clean(document.content)
        embeddings = self.embedding_generator.generate(cleaned_text)
        entities = self.entity_extractor.extract_entities(cleaned_text)
        summary = self.summarizer.summarize(cleaned_text)

        analysis = Analysis(
            document_id=document.id,
            syntax_nodes=entities,
            embeddings=embeddings,
            metadata={
                "summary": summary
            }
        )

        return analysis
