import unicodedata
import re
from typing import Optional

class TextNormalizer:
    def normalize(self, text: str) -> str:
        """Normaliza el texto eliminando espacios extras y acentos."""
        # Eliminar espacios en blanco al inicio y al final
        normalized_text = text.strip()
        # Convertir a minúsculas
        normalized_text = normalized_text.lower()
        # Eliminar acentos
        normalized_text = unicodedata.normalize('NFKD', normalized_text)
        normalized_text = ''.join([c for c in normalized_text if not unicodedata.combining(c)])
        # Reemplazar múltiples espacios por uno
        normalized_text = re.sub(r'\s+', ' ', normalized_text)
        return normalized_text