import re

class TextCleaner:
    def clean(self, text: str) -> str:
        """Limpia el texto eliminando caracteres especiales."""
        # Eliminar caracteres no alfanuméricos excepto espacios y puntuación básica
        cleaned_text = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúñÑ0-9\s.,;:!?¿¡]', '', text)
        return cleaned_text