from typing import Dict, List
import spacy
from .cleaner import TextCleaner

class TextProcessor:
    """
    Procesador principal de texto que prepara los documentos 
    para el servicio de embeddings.
    """
    def __init__(self):
        self.nlp = spacy.load('es_core_news_lg')
        self.cleaner = TextCleaner()

    async def process_text(self, text: str, doc_id: str) -> Dict:
        """
        Procesa el texto y lo prepara para embeddings.
        """
        # Limpieza inicial del texto
        cleaned_text = self.cleaner.clean_text(text)
        
        # Procesamiento con spaCy
        doc = self.nlp(cleaned_text)
        
        # Extraer párrafos significativos
        paragraphs = self._extract_paragraphs(doc)
        
        # Preparar estructura para el servicio de embeddings
        processed_data = {
            'doc_id': doc_id,
            'paragraphs': paragraphs,
            'metadata': {
                'language': doc.lang_,
                'n_paragraphs': len(paragraphs),
                'total_tokens': len(doc)
            }
        }
        
        return processed_data

    def _extract_paragraphs(self, doc) -> List[Dict]:
        """
        Extrae párrafos significativos y los prepara para embeddings.
        """
        paragraphs = []
        current_paragraph = []

        for sent in doc.sents:
            # Filtrar oraciones no significativas
            if self._is_significant_sentence(sent):
                current_paragraph.append(sent.text)
                
                if self._is_paragraph_break(sent):
                    if current_paragraph:
                        paragraphs.append({
                            'text': ' '.join(current_paragraph),
                            'tokens': self._extract_tokens(current_paragraph)
                        })
                        current_paragraph = []

        return paragraphs

    def _is_significant_sentence(self, sent) -> bool:
        """
        Determina si una oración es significativa para el análisis.
        """
        # Filtrar oraciones muy cortas o sin contenido significativo
        return (len(sent) > 5 and 
                any(token.pos_ in ['NOUN', 'VERB'] for token in sent))

    def _extract_tokens(self, paragraph: List[str]) -> List[Dict]:
        """
        Extrae tokens relevantes para el análisis.
        """
        tokens = []
        doc = self.nlp(' '.join(paragraph))
        
        for token in doc:
            if self._is_relevant_token(token):
                tokens.append({
                    'text': token.text,
                    'lemma': token.lemma_,
                    'pos': token.pos_,
                    'is_stop': token.is_stop
                })
                
        return tokens