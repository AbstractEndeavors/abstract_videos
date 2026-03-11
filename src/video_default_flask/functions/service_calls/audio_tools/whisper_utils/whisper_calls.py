from .routes import *

# whisper_calls.py
from .whisper_pipeline import WhisperPipeline
from .routes import safe_read_from_json, get_result_from_data

def get_whisper_result_data(**kwargs):
    return WhisperPipeline(kwargs).run()

def get_whisper_text(**kwargs):
    # still called get_whisper_text, but now driven by the pipeline
    data = get_whisper_result_data(**kwargs)
    return get_result_from_data("text", lambda **k: data, **kwargs)

def get_whisper_segment(**kwargs):
    data = get_whisper_result_data(**kwargs)
    return get_result_from_data("segments", lambda **k: data, **kwargs)

def get_recieve_whisper_data(data, **kwargs):
    # you likely won’t need this anymore, pipeline.save() covers it
    return safe_save_updated_json_data(
        data,
        WhisperPipeline(kwargs)._result_path(),
        valid_keys=VALID_KEYS,
        invalid_keys=INVALID_KEYS,
    )

def is_whisper_data(**info_data):
    return WhisperPipeline(info_data).exists()
