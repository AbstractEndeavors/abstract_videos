import os
import glob
import logging
import json
import sys
import spacy
from datetime import timedelta, datetime
from collections import Counter
from multiprocessing import Process

from transformers import pipeline
from keybert import KeyBERT
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

from abstract_utilities import *

def eatAllQuotes(string):
    return eatAll(string,['"',"'",'`']).replace('" "',' ')
# Initialize
logger = get_logFile('vid_to_aud')
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization", model="Falconsai/text_summarization")
keyword_extractor = pipeline("feature-extraction", model="distilbert-base-uncased")
kw_model = KeyBERT(model=keyword_extractor.model)
