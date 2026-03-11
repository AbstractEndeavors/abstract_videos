from keybert import KeyBERT
from transformers import pipeline
import torch,os,json,unicodedata,hashlib
from transformers import LEDTokenizer,LEDForConditionalGeneration
summarizer = pipeline("summarization", model="Falconsai/text_summarization")
keyword_extractor = pipeline("feature-extraction", model="distilbert-base-uncased")
generator = pipeline('text-generation', model='distilgpt2', device= -1)
kw_model = KeyBERT(model=keyword_extractor.model)


