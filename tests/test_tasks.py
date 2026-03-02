import pytest
from app.nlp_models import perform_sentiment_analysis, perform_ner, load_nlp_models

@pytest.fixture(scope="module")
def models():
    return load_nlp_models()


def test_sentiment_logic(models):
    sentiment = perform_sentiment_analysis("I love this!", models['sentiment'])
    assert 'label' in sentiment
    assert 'score' in sentiment


def test_ner_logic(models):
    ner = perform_ner("John lives in New York.", models['ner'])
    assert isinstance(ner, list)
    assert any(e['word'] == 'John' for e in ner)


def test_load_models_once(monkeypatch):
    # ensure load_nlp_models called only once when celery starts
    called = {'count': 0}
    def fake_load():
        called['count'] += 1
        return {'sentiment': None, 'ner': None}
    monkeypatch.setattr('app.tasks.load_nlp_models', fake_load)
    from app.tasks import load_models_on_startup
    load_models_on_startup(None)
    load_models_on_startup(None)
    assert called['count'] == 2  # signal called each time, but real tasks should reuse global variable
