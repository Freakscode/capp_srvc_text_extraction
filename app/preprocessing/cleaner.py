class TextCleaner:
    def clean(self, text: str) -> str:
        # Implementar lógica de limpieza de texto
        cleaned_text = text.lower()
        cleaned_text = ''.join(char for char in cleaned_text if char.isalnum() or char.isspace())
        return cleaned_text
