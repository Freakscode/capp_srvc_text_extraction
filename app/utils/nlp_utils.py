from typing import List, Dict
from cleantext import clean


def tokenize_text(text: str) -> List[str]:
    # Implementa la tokenización
    # Ejemplo simple:
    return text.split()

def remove_stopwords(tokens: List[str], stopwords: set) -> List[str]:
    return [token for token in tokens if token.lower() not in stopwords]

def lemmatize_tokens(tokens: List[str]) -> List[str]:
    # Implementa la lematización usando, por ejemplo, spaCy
    import spacy
    nlp = spacy.load('es_core_news_sm')
    doc = nlp(' '.join(tokens))
    return [token.lemma_ for token in doc]

def preprocess_text(text: str, stopwords: set) -> str:
    """Preprocesa el texto: tokenización, eliminación de palabras vacías y lematización."""
    tokens = tokenize_text(text)
    tokens = remove_stopwords(tokens, stopwords)
    tokens = lemmatize_tokens(tokens)
    return ' '.join(tokens)


def limpiar_y_normalizar_texto(texto: str) -> str:
    """
    Limpia y normaliza el texto extraído.

    Args:
        texto (str): Texto bruto extraído del PDF.

    Returns:
        str: Texto limpio y normalizado.
    """
    texto_limpio = clean(
        texto,
        fix_unicode=True,  # Arregla problemas de codificación Unicode
        to_ascii=False,    # No convierte caracteres Unicode a ASCII
        lower=True,        # Convierte el texto a minúsculas
        no_line_breaks=True,  # Elimina saltos de línea
        no_urls=True,      # Elimina URLs
        no_emails=True,    # Elimina direcciones de correo electrónico
        no_phone_numbers=True,  # Elimina números de teléfono
        no_numbers=False,  # No elimina números
        no_digits=False,   # No elimina dígitos
        no_currency_symbols=True,  # Elimina símbolos de moneda
        no_punct=True,     # Elimina puntuación
        replace_with_punct="",  # Reemplaza la puntuación con nada
        replace_with_url="<URL>",
        replace_with_email="<EMAIL>",
        replace_with_phone_number="<PHONE>",
        replace_with_number="<NUMBER>",
        replace_with_digit="0",
        replace_with_currency_symbol="<CUR>",
        lang="es"          # Especifica el idioma del texto
    )
    return texto_limpio