import os
import whisper
from pydub import AudioSegment
from pydub.silence import split_on_silence
from .whisper_services import *
from .routes import *
def get_result_path(pathname, info_data=None, **kwargs):
    # merge either top-level kwargs or the nested dict
    data = {**(info_data or {}), **kwargs}
    info_dir = get_video_info_dir(**data)
    return os.path.join(info_dir, pathname)
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
def get_whisper_input_keys():
     keys = ['audio_path',
            'model_size',
            'language',
            'use_silence',
            'info_data']
     return keys
def get_whisper_key_vars(req=None,info_data=None):
    keys = get_whisper_input_keys()
    new_data,info_data = get_key_vars(keys=keys,
                                      req=req,
                                      info_data=info_data
                                      )
    return new_data,info_data
def get_whisper_bool_key(req=None,info_data=None):
    new_data,info_data = get_whisper_key_vars(req=req,info_data=info_data)
    bool_response = is_whisper_data(**info_data)
    return get_bool_response(bool_response,info_data),info_data
def transcribe_with_wisper_call(req=None,info_data=None):
    bool_key,info_data = get_whisper_bool_key(req=req,info_data=info_data)
    function = get_transcribe_with_whisper_local_info_data
    return function,bool_key
def get_whisper_execution_variables(req=None,info_data=None):
    keys = get_whisper_input_keys()
    function,bool_key = transcribe_with_wisper_call(req=req,info_data=info_data)
    return keys,function,bool_key


class WhisperPipeline:
    def __init__(self, new_data: dict, parent_info=None):
        # if parent_info was None, default it:
        self.new_data = new_data
        parent_info = parent_info or {}
        # combine them so both sets of keys live together
        self.info = {**parent_info, **new_data}
        
        # now this will never be None
        self.directory = (
            self.info.get('info_dir')
            or self.info.get('info_directory')
            or os.path.dirname(self.info.get('info_path', ''))
        )
        self.audio_path = self.info.get('audio_path')
        self.model_size = self.info.get('model_size',"tiny")
        self.language = self.info.get('language',"english")
        self.use_silence = self.info.get('use_silence',"True")
        self.video_id = self.info.get('video_id') or os.path.basename(self.directory)
        self.file_path = os.path.join(self.directory, 'whisper_result.json')
    def _result_path(self) -> str:
        
        return self.file_path

    def load(self) -> dict | None:
        return safe_read_from_json(self.file_path)

    def exists(self) -> bool:
        return os.path.isfile(self.file_path)

    def transcribe(self) -> dict:
        self.transcript_data = transcribe_with_whisper_local(audio_path=self.audio_path,
                                                             model_size=self.model_size,
                                                             language=self.language,
                                                             use_silence=self.use_silence)
        return self.transcript_data

    def save(self, result: dict):
        safe_save_updated_json_data(
            self.transcript_data,
            self.file_path,
            valid_keys=VALID_KEYS,
            invalid_keys=INVALID_KEYS,
        )

    def export_srt(self, output_path: str | None = None):
        data = safe_load_from_json(self.file_path)
        export_srt_whisper(data, output_path or self.directory)

    def run(self) -> dict:
        self.info = update_json_data(self.info, self.info, keys=True)
        if not self.exists():
            self.transcript_data = self.transcribe()
            safe_dump_to_json(data=self.transcript_data,file_path=self.file_path)
        self.info = update_json_data(self.info, self.info, keys=True)
        return self.info
    
def execute_whisper_transcription_call(req=None, info_data=None):
    # 1) pull out the whisper inputs (audio_path, model_size, etc.)
    new_data, info_data = get_whisper_key_vars(req=req, info_data=info_data)  # :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}

    # 2) decide if we need to run (same as your bool-utils approach)
    should_run, info_data = get_whisper_bool_key(req=req, info_data=info_data)  # :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}
    if should_run:
        # 3) run the pipeline, which returns {'text':…, 'segments':…}
        pipeline = WhisperPipeline(new_data, info_data) 
        info = pipeline.run()
        info_data = update_json_data(info_data, info, keys=True)
        # 4) merge the result back into info_data
    info_data = update_json_data(info_data, new_data, keys=True)
    logger.info(f" for execute_video_text_variables ||| THIS IS THE GODDAMN INF FUCKING DATA{info_data}")
    return info_data

