# app/domain/entities/document.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class SyntaxNode:
    """Representa un nodo sintáctico en el documento"""
    text: str
    start_pos: int
    end_pos: int
    type: str  # 'sentence', 'paragraph', etc.
    syntactic_info: Dict
    confidence: float

@dataclass
class DocumentSection:
    """Representa una sección del documento con su análisis"""
    content: str
    position: Dict[str, int]  # {page, start_pos, end_pos}
    syntax_tree: List[SyntaxNode]
    metadata: Dict

@dataclass
class Document:
    id: str
    filename: str
    created_at: datetime
    sections: List[DocumentSection]
    embeddings: Optional[List[float]] = None
    metadata: Dict = None