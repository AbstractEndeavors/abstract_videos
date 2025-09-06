# whisper_pipeline.py
import os
import whisper
from pydub import AudioSegment
from pydub.silence import split_on_silence

from .routes import (
    safe_read_from_json,
    safe_save_updated_json_data,
    VALID_KEYS,
    INVALID_KEYS,
)
from .whisper_services import *
def get_result_path(pathname, info_data=None, **kwargs):
    # merge either top-level kwargs or the nested dict
    data = {**(info_data or {}), **kwargs}
    info_dir = get_video_info_dir(**data)
    return os.path.join(info_dir, pathname)

def transcribe_with_whisper_local(
    audio_path: str,
    model_size: str = "tiny",           # one of "tiny", "base", "small", "medium", "large"
    language: str = "english",
    use_silence=True,
    info_data=None):
    info_data =info_data or {}
    audio_path = audio_path or os.getcwd()
    if audio_path and os.path.isdir(audio_path):
        audio_path = os.path.join(audio_path,'audio.wav')
    info_data =info_data or {}
    # parameters for fixed chunki)
    """
    Returns the full transcript as a string.
    """
    model = whisper.load_model(model_size)           # loads to GPU if available
    # options: you can pass `task="translate"` for translating to English
 
    result = model.transcribe(audio_path, language=language)
    return result

class WhisperPipeline:
    def __init__(self, info_data: dict):
        """
        info_data should include:
          - audio_path
          - model_size
          - language
          - use_silence (bool)
          - info_data (nested dict containing at least video_id / TEXT_DIR)
          - (optional) chunk and silence params
        """
        self.info = info_data

    def _result_path(self) -> str:
        return get_result_path("whisper_result.json", info_data=self.info)

    def load(self) -> dict | None:
        return safe_read_from_json(self._result_path())

    def exists(self) -> bool:
        return self.load() is not None

    def transcribe(self) -> dict:
        model = whisper.load_model(self.info["model_size"])
        audio_path = self.info["audio_path"]
        result = transcribe_with_whisper_local(
            audio_path=audio_path,
            model_size= "tiny",           # one of "tiny", "base", "small", "medium", "large"
            language= "english",
            use_silence=True,
            info_data=None)
        return result

    def save(self, result: dict):
        safe_save_updated_json_data(
            result,
            self._result_path(),
            valid_keys=VALID_KEYS,
            invalid_keys=INVALID_KEYS,
        )

    def export_srt(self, output_path: str | None = None):
        data = self.load() or {}
        export_srt_whisper(data, output_path or os.path.dirname(self._result_path()))

    def run(self) -> dict:
        if not self.exists():
            result = self.transcribe()
            self.save(result)
        return self.load() or {}
