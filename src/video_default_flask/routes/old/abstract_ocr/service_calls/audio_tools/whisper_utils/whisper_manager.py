import os
from .whisper_call_schema import get_whisper_input_keys, get_whisper_bool_key
from .routes import get_key_vars, get_video_info_path
from .whisper_pipeline import WhisperPipeline
from abstract_utilities import safe_dump_to_file


class WhisperManager:
    """
    Orchestrates the Whisper transcription step:
      1) pulls input vars,
      2) checks if transcription is needed,
      3) runs the WhisperPipeline,
      4) merges results into info_data,
      5) persists updated info_data.
    """
    def fetch_vars(self, req=None, info_data=None):
        keys = get_whisper_input_keys()
        new_data, info_data = get_key_vars(keys, req=req, info_data=info_data)
        return new_data, info_data

    def should_run(self, req=None, info_data=None):
        # get_whisper_bool_key returns (bool_flag, possibly-updated info_data)
        should_run, info_data = get_whisper_bool_key(req=req, info_data=info_data)
        return should_run, info_data

    def run(self, req=None, info_data=None):
        # 1) gather inputs
        new_data, info_data = self.fetch_vars(req=req, info_data=info_data)
        # 2) decide if we need to transcribe
        run_flag, info_data = self.should_run(req=req, info_data=info_data)
        if not run_flag:
            return info_data

        # 3) run the pipeline (handles model load, transcription, and saving whisper_result.json)
        pipeline = WhisperPipeline(info_data)
        result = pipeline.run()

        # 4) merge result (text, segments, etc.) into our aggregated info_data
        info_data.update(result)

        # 5) persist the full info_data back into info.json
        path = get_video_info_path(**info_data)
        safe_dump_to_file(data=info_data, file_path=path)

        return info_data
