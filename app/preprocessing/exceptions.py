class PDFProcessingError(Exception):
    """Excepción personalizada para errores en el procesamiento de PDF."""
    
    def __init__(self, message: str):
        super().__init__(message)