# FastAPI NLP Microservice

Este proyecto es un microservicio desarrollado con FastAPI que se encarga de realizar procesamientos de Procesamiento de Lenguaje Natural (NLP). A continuación se detallan las características y la estructura del proyecto.

## Estructura del Proyecto


```
fastapi-nlp-microservice ├── app │ ├── main.py # Punto de entrada de la aplicación │ ├── api │ │ └── v1 │ │ └── endpoints │ │ └── nlp.py # Rutas para el procesamiento de NLP │ ├── core │ │ └── config.py # Configuración de la aplicación │ ├── models │ │ └── nlp_model.py # Modelos de datos para NLP │ ├── schemas │ │ └── nlp_schema.py # Esquemas de validación de datos │ ├── services │ │ └── nlp_service.py # Lógica de negocio para NLP │ └── utils │ └── nlp_utils.py # Funciones utilitarias para NLP ├── tests │ ├── test_nlp.py # Pruebas unitarias para el microservicio ├── requirements.txt # Dependencias del proyecto ├── Dockerfile # Imagen de Docker para el microservicio └── README.md
```

# Documentación del proyecto

## Instalación

1. Clona el repositorio:
   ```
   git clone <URL_DEL_REPOSITORIO>
   cd fastapi-nlp-microservice
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

Para ejecutar el microservicio, utiliza el siguiente comando:
```
uvicorn app.main:app --reload
```

Esto iniciará el servidor en `http://127.0.0.1:8000`.

## Pruebas

Para ejecutar las pruebas unitarias, utiliza:
```
pytest tests/test_nlp.py
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para discutir cambios.

## Licencia

Este proyecto está bajo la Licencia MIT.