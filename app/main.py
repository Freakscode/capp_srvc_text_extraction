import logging
from fastapi import FastAPI
from app.api.v1.endpoints import nlp

app = FastAPI()

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,  # Cambia a DEBUG para más detalles si es necesario
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Incluir el router de NLP
app.include_router(nlp.router, prefix="/api/v1/nlp")

@app.get("/")
def read_root():
    return {"message": "Microservicio NLP funcionando correctamente"}