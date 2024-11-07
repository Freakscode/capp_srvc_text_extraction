from typing import Dict, List, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor
import spacy
from pdfminer.high_level import extract_pages
from pdfminer.layout import (
    LTTextContainer, LTChar, LTLine, 
    LTFigure, LTTable, LAParams,
    LTTextBox, LTTextBoxHorizontal
)
from .exceptions import PDFProcessingError

class PDFExtractor:
    def __init__(self, cache_dir: Optional[str] = None):
        """Inicializa el extractor de PDF con opciones avanzadas"""
        self._setup_logging()
        self._load_models(cache_dir)
        self._setup_processors()
        self._initialize_thread_pool()
        
    def _setup_logging(self):
        """Configura el sistema de logging"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def _load_models(self, cache_dir: Optional[str]):
        """Carga modelos NLP con manejo de errores mejorado"""
        try:
            if cache_dir:
                spacy.prefer_gpu()
                self.nlp_es = spacy.load('es_core_news_lg', disable=['ner'])
                self.nlp_en = spacy.load('en_core_web_sm', disable=['ner'])
                self.nlp_es.max_length = 2000000
                self.nlp_en.max_length = 2000000
            else:
                self.logger.warning("No se especificó directorio de caché")
                self.nlp_es = spacy.load('es_core_news_lg')
                self.nlp_en = spacy.load('en_core_web_sm')
        except OSError as e:
            self.logger.error(f"Error cargando modelos NLP: {e}")
            raise PDFProcessingError(f"Error en carga de modelos: {str(e)}")
            
    def _setup_processors(self):
        """Configura parámetros de procesamiento PDF"""
        self.la_params = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            boxes_flow=0.5,
            detect_vertical=True,
            all_texts=True,
            paragraph_indent=2.0,
            line_overlap=0.5,
            line_spacing=0.5,
        )
        
        self.processors = {
            'text': self._process_text_element,
            'table': self._process_table,
            'figure': self._process_figure
        }
        
    def _initialize_thread_pool(self):
        """Inicializa pool de hilos para procesamiento paralelo"""
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def extract_document(self, pdf_path: str) -> Dict:
        """Punto de entrada principal para extracción de documento"""
        try:
            self.logger.info(f"Iniciando procesamiento de {pdf_path}")
            
            result = {
                'metadata': self._extract_metadata(pdf_path),
                'content': [],
                'structure': [],
                'tables': [],
                'figures': [],
                'statistics': {}
            }
            
            pages = list(extract_pages(pdf_path, laparams=self.la_params))
            futures = []
            
            for page_num, page in enumerate(pages):
                future = self.executor.submit(
                    self._process_page, 
                    page, 
                    page_num
                )
                futures.append(future)
                
            for future in futures:
                page_result = future.result()
                result['content'].extend(page_result['content'])
                result['tables'].extend(page_result['tables'])
                result['figures'].extend(page_result['figures'])
                result['structure'].append(page_result['structure'])
                
            result['statistics'] = self._calculate_statistics(result)
            
            self.logger.info(f"Procesamiento completado: {pdf_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error procesando {pdf_path}: {e}")
            raise PDFProcessingError(f"Error en procesamiento: {str(e)}")
            
    def _process_page(self, page, page_num: int) -> Dict:
        """Procesa una página individual del PDF"""
        result = {
            'content': [],
            'tables': [],
            'figures': [],
            'structure': {
                'page_num': page_num,
                'layout': self._analyze_page_layout(page)
            }
        }
        
        for element in page:
            processor = self.processors.get(element.__class__.__name__.lower())
            if processor:
                processed = processor(element, page)
                if processed:
                    if 'text' in processed:
                        result['content'].append(processed)
                    elif 'table' in processed:
                        result['tables'].append(processed['table'])
                    elif 'figure' in processed:
                        result['figures'].append(processed['figure'])
                    
        return result
            
    def _process_text_element(self, element, page) -> Optional[Dict]:
        """Procesa elemento de texto con análisis detallado"""
        text = element.get_text().strip()
        if not text:
            return None
        
        return {
            'text': text,
            'position': self._get_element_position(element, page),
            'style': self._extract_style_info(element),
            'hierarchy': self._detect_hierarchy(element, text),
            'language': self._detect_language(text),
            'column': self._detect_column(element, page),
            'type': self._detect_element_type(element, text)
        }
        
    def _extract_style_info(self, element) -> Dict:
        """Extrae información detallada de estilo"""
        chars = [c for c in element if isinstance(c, LTChar)]
        if not chars:
            return {}
            
        return {
            'font': {
                'name': chars[0].fontname,
                'size': round(chars[0].size, 2),
                'family': self._extract_font_family(chars[0].fontname)
            },
            'style': {
                'bold': 'Bold' in chars[0].fontname,
                'italic': 'Italic' in chars[0].fontname,
                'color': self._extract_color(chars[0])
            },
            'metrics': {
                'line_height': self._calculate_line_height(element),
                'char_spacing': self._calculate_char_spacing(chars)
            }
        }

    def close(self):
        """Limpia recursos"""
        self.executor.shutdown()