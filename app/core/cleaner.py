import re
from typing import List

class TextCleaner:
    """
    Limpieza y normalización de texto.
    """
    def clean_text(self, text: str) -> str:
        """
        Limpia y normaliza el texto.
        """
        # Normalización básica
        text = self._normalize_whitespace(text)
        text = self._remove_special_chars(text)
        text = self._normalize_quotes(text)
        
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """
        Normaliza espacios en blanco y saltos de línea.
        """
        # Reemplazar múltiples espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        # Normalizar saltos de línea
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
