class NLPResult:
    def __init__(self, text: str, coordinates: dict, syntactic_analysis: dict):
        self.text = text
        self.coordinates = coordinates
        self.syntactic_analysis = syntactic_analysis

    def to_dict(self):
        return {
            "text": self.text,
            "coordinates": self.coordinates,
            "syntactic_analysis": self.syntactic_analysis
        }
