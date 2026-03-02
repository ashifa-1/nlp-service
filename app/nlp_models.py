import spacy
from transformers import pipeline

# Load models for sentiment analysis and named entity recognition

def load_nlp_models():
    models = {}
    # sentiment analysis via Hugging Face
    models['sentiment'] = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        tokenizer="distilbert-base-uncased-finetuned-sst-2-english"
    )
    # named entity recognition via Hugging Face
    models['ner'] = pipeline(
        "ner",
        grouped_entities=True,
        model="dbmdz/bert-large-cased-finetuned-conll03-english",
        tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english"
    )
    # optionally include spaCy model for general use
    # try:
    #     models['spacy_general'] = spacy.load("en_core_web_sm")
    # except OSError:
    #     spacy.cli.download("en_core_web_sm")
    #     models['spacy_general'] = spacy.load("en_core_web_sm")
    return models


def perform_sentiment_analysis(text: str, sentiment_pipeline) -> dict:
    result = sentiment_pipeline(text)[0]
    return {"label": result['label'], "score": result['score']}


def perform_ner(text: str, ner_pipeline) -> list:
    entities = ner_pipeline(text)
    formatted = []
    for ent in entities:
        formatted.append({
            "entity_group": ent.get('entity_group'),
            "word": ent.get('word'),
            "score": ent.get('score'),
            "start": ent.get('start'),
            "end": ent.get('end')
        })
    return formatted
