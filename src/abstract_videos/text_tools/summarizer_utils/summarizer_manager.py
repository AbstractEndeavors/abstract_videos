# summarizer_manager.py

import os
from transformers import pipeline
from .summarizer_call_schema import get_summary_input_keys
from .summarizer_get_data import get_summary_data
from .routes import *
from abstract_utilities import safe_dump_to_file


class SummarizerManager:
    def __init__(self, model_name="Falconsai/text_summarization", device=-1):
        # 1) single pipeline instance
        self.summarizer = pipeline("summarization", model=model_name, device=device)

    def should_run(self, info_data):
        # reuse your boolean check + wrap it in your get_bool_response
        bool_key = info_data.get("summary") is None
        return get_bool_response(bool_key, info_data)

    def fetch_inputs(self, req=None, info_data=None):
        # pulls just “keywords” & “full_text” out of your request/info
        keys = get_summary_input_keys()
        new_data, info_data = get_key_vars(keys, req=req, info_data=info_data)
        return new_data, info_data

    def run(self, req=None, info_data=None):
        new_data = info_data
        #new_data, info_data = self.fetch_inputs(req, info_data)

        # 2) should we even summarize?
        if not self.should_run(info_data):
            return info_data

        # 3) invoke your existing get_summary_data under the hood—
        #    we just inject our own pipeline
        result = get_summary_data(
            summarizer=self.summarizer,
            full_text=new_data["full_text"],
            keywords=new_data["keywords"]
        )

        # 4) stash it
        info_data["summary"] = result

        # 5) persist immediately
        path = get_video_info_path(**info_data)
        safe_dump_to_file(
            data=info_data,
            file_path=path
        )
        return info_data
