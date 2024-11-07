import re
from typing import Optional

class TextCleaner:
    def clean(self, text: str) -> str:
        """Limpia el texto eliminando caracteres no deseados y normalizando espacios."""
        # Convertir a minúsculas
        cleaned_text = text.lower()
        # Eliminar caracteres no alfanuméricos excepto espacios
        cleaned_text = re.sub(r'[^a-z0-9\s]', '', cleaned_text)
        # Reemplazar múltiples espacios por uno
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        # Eliminar espacios al inicio y al final
        cleaned_text = cleaned_text.strip()
        return cleaned_text