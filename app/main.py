# app/main.py

from fastapi import FastAPI
from app.api.v1.endpoints import nlp

app = FastAPI(title="Microservicio de NLP")

app.include_router(nlp.router, prefix="/api/v1/nlp", tags=["nlp"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido al microservicio de procesamiento de NLP"}