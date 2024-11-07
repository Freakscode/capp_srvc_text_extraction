from typing import Dict, List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
import spacy
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.high_level import extract_pages
from pdfminer.layout import (
    LTTextContainer, LTChar, LTLine, 
    LTFigure, LTImage, LAParams,
    LTTextBox, LTTextBoxHorizontal
)
from langdetect import detect, LangDetectException
import os
from .exceptions import PDFProcessingError  # Asegúrate de que esta excepción esté definida


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
            all_texts=True
        )
        self.processors = {
            'lttextcontainer': self._process_text_element,
            'ltchar': self._process_text_element,
            'ltline': self._process_line_element,
            'ltfigure': self._process_figure,
            'ltimage': self._process_image,
            'lttextbox': self._process_text_element,
            'lttextboxhorizontal': self._process_text_element
        }

    def _initialize_thread_pool(self):
        """Inicializa pool de hilos para procesamiento paralelo"""
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _extract_metadata(self, pdf_path: str) -> Dict:
        """Extrae metadatos del PDF."""
        metadata = {}
        try:
            with open(pdf_path, 'rb') as f:
                parser = PDFParser(f)
                document = PDFDocument(parser)
                
                if document.info:
                    doc_info = document.info[0]
                    for key, value in doc_info.items():
                        if isinstance(key, bytes):
                            clean_key = key.decode('utf-8').lstrip('/')
                        else:
                            clean_key = key.lstrip('/')
                        
                        if isinstance(value, bytes):
                            clean_value = value.decode('utf-8', errors='ignore')
                        else:
                            clean_value = value
                        
                        metadata[clean_key] = clean_value
        except Exception as e:
            self.logger.error(f"Error extrayendo metadatos: {e}")
            metadata = {}
        
        return metadata

    def _analyze_page_layout(self, page) -> Dict:
        """Analiza la disposición de una página del PDF."""
        layout_info = {
            'text_boxes': [],
            'images': [],
            'figures': []
        }
        
        try:
            for element in page:
                if isinstance(element, LTTextBox) or isinstance(element, LTTextBoxHorizontal):
                    text_info = {
                        'x0': element.x0,
                        'y0': element.y0,
                        'x1': element.x1,
                        'y1': element.y1,
                        'text': element.get_text().strip()
                    }
                    layout_info['text_boxes'].append(text_info)
                
                elif isinstance(element, LTImage):
                    image_info = {
                        'x0': element.x0,
                        'y0': element.y0,
                        'x1': element.x1,
                        'y1': element.y1,
                        'name': element.name,
                        'stream': element.stream.get_rawdata() if element.stream else None
                    }
                    layout_info['images'].append(image_info)
                
                elif isinstance(element, LTFigure):
                    figure_info = {
                        'x0': element.x0,
                        'y0': element.y0,
                        'x1': element.x1,
                        'y1': element.y1,
                        'content': self._extract_figure_content(element)
                    }
                    layout_info['figures'].append(figure_info)
        except Exception as e:
            self.logger.error(f"Error analizando disposición de página: {e}")
        
        return layout_info

    def _extract_figure_content(self, figure) -> List[Dict]:
        """Extrae contenido de una figura."""
        figures = []
        for element in figure:
            if isinstance(element, LTImage):
                image_info = {
                    'x0': element.x0,
                    'y0': element.y0,
                    'x1': element.x1,
                    'y1': element.y1,
                    'name': element.name,
                    'stream': element.stream.get_rawdata() if element.stream else None
                }
                figures.append(image_info)
        return figures

    def _process_page(self, page, page_num: int) -> Dict:
        """Procesa una página individual del PDF"""
        result = {
            'content': [],
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
                    elif 'figure' in processed:
                        result['figures'].append(processed['figure'])
                    elif 'line' in processed:
                        result['content'].append(processed)
                    elif 'image' in processed:
                        result['images'].append(processed['image'])
                    
        return result

    def _process_text_element(self, element, page) -> Optional[Dict]:
        """Procesa elemento de texto con análisis detallado"""
        text = element.get_text().strip()
        if not text:
            return None
        
        text_parts = []
        if isinstance(element, LTTextContainer):
            for text_line in element:
                line_text = text_line.get_text().strip()
                for char in text_line:
                    if isinstance(char, LTChar):
                        text_parts.append(line_text)
                        break
        text = ' '.join(text_parts) if text_parts else text
        
        style_info = self._extract_style_info(element)
        hierarchy = self._detect_hierarchy(element, text)
        language = self._detect_language(text)
        column = self._detect_column(element, page)
        element_type = self._detect_element_type(element, text)
        
        return {
            'text': text,
            'position': self._get_element_position(element, page),
            'style': style_info,
            'hierarchy': hierarchy,
            'language': language,
            'column': column,
            'type': element_type
        }
        
    def _process_line_element(self, element, page) -> Optional[Dict]:
        """Procesa elementos de línea en el PDF."""
        line_info = {
            'position': self._get_element_position(element, page)
            # Puedes agregar más información si es necesario
        }
        return {
            'line': line_info
        }

    def _process_figure(self, element, page) -> Optional[Dict]:
        """Procesa elementos de figura en el PDF."""
        try:
            figure_data = self._extract_figure_content(element)
            return {
                "figure": {
                    "type": "figure",
                    "content": figure_data,
                    "position": self._get_element_position(element, page)
                }
            }
        except Exception as e:
            self.logger.error(f"Error procesando figura: {e}")
            return None

    def _process_image(self, element, page) -> Optional[Dict]:
        """Procesa elementos de imagen en el PDF."""
        try:
            image_data = {
                'name': element.name,
                'position': self._get_element_position(element, page),
                'stream': element.stream.get_rawdata() if element.stream else None
            }
            return {
                "image": image_data
            }
        except Exception as e:
            self.logger.error(f"Error procesando imagen: {e}")
            return None

    def _get_element_position(self, element, page) -> Dict:
        """Obtiene la posición de un elemento en la página."""
        return {
            'x0': element.x0,
            'y0': element.y0,
            'x1': element.x1,
            'y1': element.y1
        }

    def _extract_style_info(self, element) -> Dict:
        """Extrae información detallada de estilo"""
        style = {}
        if isinstance(element, LTTextContainer):
            for text_line in element:
                for char in text_line:
                    if isinstance(char, LTChar):
                        style['fontname'] = char.fontname
                        style['size'] = char.size
                        style['bold'] = 'Bold' in char.fontname
                        style['italic'] = 'Italic' in char.fontname
                        break
                break
        return style

    def _detect_hierarchy(self, element, text: str) -> str:
        """Detecta la jerarquía del texto."""
        font_sizes = []
        if isinstance(element, LTTextContainer):
            for text_line in element:
                for char in text_line:
                    if isinstance(char, LTChar):
                        font_sizes.append(char.size)
        average_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
        if average_size > 14:
            return 'title'
        elif 12 < average_size <= 14:
            return 'subtitle'
        else:
            return 'body'

    def _detect_language(self, text: str) -> str:
        """Detecta el idioma del texto."""
        try:
            lang = detect(text)
            return lang
        except LangDetectException:
            return 'unknown'

    def _detect_column(self, element, page) -> int:
        """Detecta la columna a la que pertenece el elemento de texto."""
        # Ejemplo de detección simple basado en la posición x0
        x0 = element.x0
        if x0 < 300:
            return 1
        elif 300 <= x0 < 600:
            return 2
        else:
            return 3

    def _detect_element_type(self, element, text: str) -> str:
        """Detecta el tipo de elemento de texto."""
        style = self._extract_style_info(element)
        if style.get('bold') and style.get('size', 0) > 14:
            return 'title'
        elif style.get('bold') and style.get('size', 0) > 12:
            return 'subtitle'
        else:
            return 'paragraph'

    def extract_document(self, pdf_path: str) -> Dict:
        try:
            self.logger.info(f"Iniciando procesamiento de {pdf_path}")
            
            result = {
                'metadata': self._extract_metadata(pdf_path),
                'content': [],
                'structure': [],
                'figures': [],
                'images': [],
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
                result['figures'].extend(page_result['figures'])
                result['structure'].append(page_result['structure'])
                # Agregar imágenes si se procesan
                for img in page_result['structure']['layout'].get('images', []):
                    result['images'].append(img)
            
            # Agregar texto completo
            result['full_text'] = self.get_full_text(result)
            result['statistics'] = self._calculate_statistics(result)
            
            self.logger.info(f"Procesamiento completado: {pdf_path}")
            self.logger.info(f"Tipo de resultado: {type(result)}")  # Agregado para depuración
            return result
                
        except Exception as e:
            self.logger.error(f"Error procesando {pdf_path}: {e}")
            raise PDFProcessingError(f"Error en procesamiento: {str(e)}")

    def _calculate_statistics(self, result: Dict) -> Dict:
        """Calcula estadísticas básicas del contenido extraído."""
        statistics = {}
        try:
            statistics['numero_paginas'] = len(result.get('structure', []))
            statistics['total_contenido'] = len(result.get('content', []))
            statistics['total_figuras'] = len(result.get('figures', []))
            statistics['total_imagenes'] = len(result.get('images', []))
            statistics['total_paragraphs'] = sum(
                1 for item in result.get('content', []) 
                if isinstance(item, dict) and item.get('type') == 'paragraph'
            )
            statistics['total_titles'] = sum(
                1 for item in result.get('content', []) 
                if isinstance(item, dict) and item.get('type') == 'title'
            )
            statistics['total_subtitles'] = sum(
                1 for item in result.get('content', []) 
                if isinstance(item, dict) and item.get('type') == 'subtitle'
            )
            statistics['total_characters'] = sum(
                len(item['text']) for item in result.get('content', []) 
                if isinstance(item, dict) and 'text' in item
            )
        except Exception as e:
            self.logger.error(f"Error calculando estadísticas: {e}")
        return statistics
    
    def get_full_text(self, result: Dict) -> str:
        """Extrae todo el texto del documento procesado."""
        text_parts = []
        for content in result.get('content', []):
            if isinstance(content, dict) and 'text' in content:
                text_parts.append(content['text'])
        return ' '.join(text_parts)
    
    def close(self):
        """Limpia recursos"""
        self.executor.shutdown()