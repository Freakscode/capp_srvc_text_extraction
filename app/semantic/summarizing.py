from transformers import pipeline

class TextSummarizer:
    def __init__(self, model_name: str = 'facebook/bart-large-cnn'):
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize(self, text: str, max_length: int = 130, min_length: int = 30, do_sample: bool = False) -> str:
        summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=do_sample)
        return summary[0]['summary_text']
