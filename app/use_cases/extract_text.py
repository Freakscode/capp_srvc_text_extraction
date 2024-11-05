import fitz  # PyMuPDF

class ExtractTextUseCase:
    def __init__(self):
        pass

    def execute(self, file_path: str) -> str:
        document = fitz.open(file_path)
        text = ""
        for page in document:
            text += page.get_text()
        return text
