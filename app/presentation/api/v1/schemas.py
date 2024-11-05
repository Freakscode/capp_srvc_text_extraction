from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class DocumentSchema(BaseModel):
    id: str
    filename: str
    created_at: datetime
    sections: List[Dict]
    embeddings: Optional[List[float]] = None
    metadata: Dict = None

class AnalysisSchema(BaseModel):
    document_id: str
    syntax_nodes: List[Dict]
    embeddings: List[float]
    metadata: Dict
