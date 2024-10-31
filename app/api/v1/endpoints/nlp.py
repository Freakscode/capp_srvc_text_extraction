# app/api/v1/endpoints/nlp.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.nlp_service import NLPService
from app.models.nlp_model import NLPResponse

router = APIRouter()
nlp_service = NLPService()

@router.post("/extract-text", response_model=NLPResponse)
async def extract_text(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = nlp_service.process_document(content)
        return NLPResponse(entities=result["analysis"]["entities"], tokens=result["analysis"]["tokens"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))