from ..routes import *
from abstract_ocr import  format_timestamp
_format_srt_timestamp = format_timestamp
import whisper
import speech_recognition as sr
from pydub import AudioSegment
r = sr.Recognizer()
import numpy as np
from abstract_utilities import (safe_save_updated_json_data,
                                get_result_from_data,
                                remove_path,
                                remove_directory,
                                make_list_it,
                                List,
                                shutil,
                                Optional)

from abstract_utilities import get_bool_response
SAMPLE_RATE = whisper.audio.SAMPLE_RATE  # 16000 Hz
def get_output_directory(info_data):
    output_dir = (
        info_data.get('info_dir') or
        info_data.get('info_directory') or
        info_data.get('output_directory') or
        info_data.get('directory') or
        os.getcwd()
        )
    return output_dir
def make_audio_dir(info_data):
    output_dir = get_output_directory(info_data)
    audio_dir = os.path.join(output_dir,'audio')
    os.makedirs(audio_dir,exist_ok=True)
    return audio_dir
def collate_trans_chunks(chunks,transcribe_func,key,full_text=None,**kwargs):
    full_text = make_list_it(full_text)
    for chunk in chunks:
        res = transcribe_func(chunk, **kwargs)
        full_text.append(res[key].strip())
    return full_text
