from ..routes import *
from keybert import KeyBERT
keyword_extractor = pipeline("feature-extraction", model="distilbert-base-uncased")
kw_model = KeyBERT(model=keyword_extractor.model)
