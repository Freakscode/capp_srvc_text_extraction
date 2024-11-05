class Analysis:
    def __init__(self, document_id: str, syntax_nodes: list, embeddings: list, metadata: dict):
        self.document_id = document_id
        self.syntax_nodes = syntax_nodes
        self.embeddings = embeddings
        self.metadata = metadata

    def to_dict(self):
        return {
            "document_id": self.document_id,
            "syntax_nodes": self.syntax_nodes,
            "embeddings": self.embeddings,
            "metadata": self.metadata
        }
