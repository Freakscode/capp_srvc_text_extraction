from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'):
        self.model = SentenceTransformer(model_name)

    def generate(self, text: str) -> list:
        embeddings = self.model.encode([text])
        return embeddings.tolist()
