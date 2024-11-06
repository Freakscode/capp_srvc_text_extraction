# app/preprocessing/pdf_extractor.py
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTLine
import spacy
from typing import Dict, List, Tuple
import re

class PDFExtractor:
    def __init__(self):
        # Cargar modelos de spaCy para español e inglés
        self.nlp_es = spacy.load('es_core_news_lg')  # Modelo grande para mejor precisión
        self.nlp_en = spacy.load('en_core_web_sm')   # Modelo pequeño para términos en inglés
        
    def extract_text_with_positions(self, pdf_path: str) -> List[Dict]:
        """Extrae texto con información de posicionamiento y estilo"""
        paragraphs = []
        
        for page_layout in extract_pages(pdf_path):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    paragraph = {
                        'text': element.get_text().strip(),
                        'position': {
                            'x0': element.x0,
                            'y0': element.y0,
                            'x1': element.x1,
                            'y1': element.y1,
                            'page_number': page_layout.pageid
                        },
                        'style': self._extract_style_info(element)
                    }
                    if paragraph['text']:
                        paragraphs.append(paragraph)
        
        return paragraphs
    
    def _extract_style_info(self, element) -> Dict:
        """Extrae información de estilo del texto"""
        chars = [c for c in element if isinstance(c, LTChar)]
        if not chars:
            return {}
            
        return {
            'font_name': chars[0].fontname,
            'font_size': round(chars[0].size, 2),
            'is_bold': 'Bold' in chars[0].fontname,
            'is_italic': 'Italic' in chars[0].fontname
        }

    def process_text(self, paragraphs: List[Dict]) -> List[Dict]:
        """Procesa el texto con análisis lingüístico"""
        processed_paragraphs = []
        
        for paragraph in paragraphs:
            # Análisis en español
            doc_es = self.nlp_es(paragraph['text'])
            
            # Detectar términos en inglés
            english_terms = self._detect_english_terms(paragraph['text'])
            
            processed_text = {
                'original': paragraph,
                'sentences': self._process_sentences(doc_es),
                'entities': self._extract_entities(doc_es),
                'english_terms': english_terms,
                'linguistic_features': self._extract_linguistic_features(doc_es)
            }
            
            processed_paragraphs.append(processed_text)
            
        return processed_paragraphs
    
    def _detect_english_terms(self, text: str) -> List[Dict]:
        """Detecta y analiza términos en inglés"""
        # Patrón para detectar posibles términos en inglés (siglas, términos técnicos)
        english_pattern = r'\b[A-Z]{2,}(?:\s[A-Z]{2,})*\b|\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b'
        potential_terms = re.finditer(english_pattern, text)
        
        english_terms = []
        for term in potential_terms:
            doc_en = self.nlp_en(term.group())
            if doc_en._.language['language'] == 'en':
                english_terms.append({
                    'term': term.group(),
                    'position': (term.start(), term.end()),
                    'analysis': {
                        'pos': doc_en[0].pos_,
                        'tag': doc_en[0].tag_,
                        'is_technical': self._is_technical_term(doc_en[0])
                    }
                })
        
        return english_terms
    
    def _process_sentences(self, doc) -> List[Dict]:
        """Procesa cada oración del texto"""
        return [{
            'text': sent.text,
            'start_char': sent.start_char,
            'end_char': sent.end_char,
            'sentiment': sent._.polarity if hasattr(sent._, 'polarity') else None,
            'key_phrases': self._extract_key_phrases(sent)
        } for sent in doc.sents]
    
    def _extract_entities(self, doc) -> List[Dict]:
        """Extrae entidades nombradas con contexto"""
        return [{
            'text': ent.text,
            'label': ent.label_,
            'start_char': ent.start_char,
            'end_char': ent.end_char,
            'context': self._get_entity_context(doc, ent)
        } for ent in doc.ents]
    
    def _extract_linguistic_features(self, doc) -> Dict:
        """Extrae características lingüísticas detalladas"""
        return {
            'tokens': [{
                'text': token.text,
                'lemma': token.lemma_,
                'pos': token.pos_,
                'tag': token.tag_,
                'dep': token.dep_,
                'is_stop': token.is_stop,
                'vector': token.vector.tolist()
            } for token in doc],
            'noun_chunks': [{
                'text': chunk.text,
                'root': chunk.root.text
            } for chunk in doc.noun_chunks]
        }
