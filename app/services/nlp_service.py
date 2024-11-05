import boto3
import fitz  # PyMuPDF
import logging
from typing import Dict
from app.utils.nlp_utils import limpiar_y_normalizar_texto
from app.core.config import settings
import spacy
from nltk.corpus import stopwords
import nltk

class NLPService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.s3_client = boto3.client('s3', region_name=settings.aws_region)
        self.nlp = spacy.load('es_core_news_sm')
        try:
            self.stopwords = set(stopwords.words('spanish'))
        except LookupError:
            nltk.download('stopwords')
            self.stopwords = set(stopwords.words('spanish'))
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')

    def extract_text(self, file: bytes) -> str:
        """Extrae texto de un archivo PDF usando PyMuPDF."""
        try:
            pdf_document = fitz.open(stream=file, filetype="pdf")
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            self.logger.debug(f"Texto extraído: {text[:100]}...")  # Muestra los primeros 100 caracteres del texto extraído
            return text
        except Exception as e:
            self.logger.error(f"Error al extraer texto: {e}")
            return ""

    def process_text(self, text: str) -> Dict:
        """Procesa el texto usando spaCy."""
        self.logger.debug(f"Texto antes de limpiar: {text[:100]}...")  # Muestra los primeros 100 caracteres del texto antes de limpiar
        preprocessed_text = limpiar_y_normalizar_texto(text)
        self.logger.debug(f"Texto después de limpiar: {preprocessed_text[:100]}...")  # Muestra los primeros 100 caracteres del texto después de limpiar
        doc = self.nlp(preprocessed_text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        tokens = [token.text for token in doc]
        return {
            "entities": entities,
            "tokens": tokens
        }

    def process_document(self, file: bytes, filename: str) -> Dict:
        """Procesa un documento completo."""
        text = self.extract_text(file)
        analysis = self.process_text(text)
        return {
            "filename": filename,
            "text": text,
            "analysis": analysis
        }