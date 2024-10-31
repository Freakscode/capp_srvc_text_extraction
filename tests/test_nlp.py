from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_nlp_endpoint():
    response = client.post("/api/v1/nlp/process", json={"text": "Hola, mundo!"})
    assert response.status_code == 200
    assert "result" in response.json()

def test_nlp_invalid_input():
    response = client.post("/api/v1/nlp/process", json={"text": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "El texto no puede estar vacío."