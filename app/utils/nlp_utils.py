import re
import unicodedata
from nltk.corpus import stopwords

def tokenize_text(text: str) -> list:
    """Divide el texto en tokens."""
    return text.split()

def remove_stopwords(tokens: list, stopwords: set) -> list:
    """Elimina las palabras vacías de la lista de tokens."""
    return [token for token in tokens if token not in stopwords]

def stem_tokens(tokens: list) -> list:
    """Aplica stemming a los tokens."""
    from nltk.stem import PorterStemmer
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

def lemmatize_tokens(tokens: list) -> list:
    """Aplica lematización a los tokens."""
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

def preprocess_text(text: str, stopwords: set) -> str:
    """Preprocesa el texto: tokenización, eliminación de palabras vacías y lematización."""
    tokens = tokenize_text(text)
    tokens = remove_stopwords(tokens, stopwords)
    tokens = lemmatize_tokens(tokens)
    return ' '.join(tokens)