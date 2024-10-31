# app/models/nlp_model.py

from pydantic import BaseModel
from typing import List, Dict

class Entity(BaseModel):
    text: str
    label: str

class NLPResponse(BaseModel):
    entities: List[Entity]
    tokens: List[str]