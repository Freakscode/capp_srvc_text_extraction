# app/models/nlp_model.py

from pydantic import BaseModel
from typing import List

class Entity(BaseModel):
    text: str
    label: str

class NLPDocumentResponse(BaseModel):
    document_id: str
    entities: List[Entity]
    tokens: List[str]

class NLPBatchResponse(BaseModel):
    documents: List[NLPDocumentResponse]