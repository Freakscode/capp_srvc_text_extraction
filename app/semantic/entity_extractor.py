import spacy

class EntityExtractor:
    def __init__(self, model_name: str = 'es_core_news_lg'):
        self.nlp = spacy.load(model_name)

    def extract_entities(self, text: str) -> list:
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "label": ent.label_
            })
        return entities
