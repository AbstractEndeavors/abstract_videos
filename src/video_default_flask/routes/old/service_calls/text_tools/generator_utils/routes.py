from ..routes import *
from transformers import LEDTokenizer,LEDForConditionalGeneration
generator = pipeline('text-generation', model='distilgpt2', device= -1)
