from pydantic import BaseModel
from typing import List, Optional

class TextInput(BaseModel):
    text: str

class TextOutput(BaseModel):
    processed_text: str
    tokens: List[str]
    sentiment: Optional[str] = None

class NLPResponse(BaseModel):
    input: TextInput
    output: TextOutput