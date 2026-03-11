from ..routes import *
import whisper
from abstract_ocr import  format_timestamp
_format_srt_timestamp = format_timestamp
import whisper
import speech_recognition as sr
from pydub import AudioSegment
r = sr.Recognizer()
import numpy as np
SAMPLE_RATE = whisper.audio.SAMPLE_RATE  # 16000 Hz
