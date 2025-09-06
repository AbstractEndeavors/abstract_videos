# keybert_manager.py

import os
from .keybert_call_schema import get_keyword_execution_variables  # :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}
from abstract_utilities import safe_dump_to_file
from .routes import get_bool_response, get_key_vars, get_video_info_path

class KeywordManager:
    """
    Orchestrates:
      1) deciding if keywords need to be run,
      2) pulling input vars,
      3) calling the keyword‐service,
      4) persisting results.
    """
    def fetch_step_vars(self, req=None, info_data=None):
        # returns (inputs_dict, info_data, service_fn, bool_key)
        keys, service_fn, bool_key = get_keyword_execution_variables(
            req=req, info_data=info_data
        )
        inputs, info_data = get_key_vars(keys, req=req, info_data=info_data)
        return inputs, info_data, service_fn, bool_key

    def should_run(self, bool_key, info_data):
        # wraps your boolean‐check helper
        return get_bool_response(bool_key, info_data)

    def run(self, req=None, info_data=None):
        # 1) Gather everything we need
        inputs, info_data, service_fn, bool_key = self.fetch_step_vars(info_data)

        # 2) Decide if we actually extract keywords
        if not self.should_run(bool_key, info_data):
            return info_data
        if 'info_data' not in inputs:
            inputs['info_data'] = info_data
        # 3) Call into keybert_get_data.get_keywords_info_data
        #    which will update info_data['keywords'], ['combined_keywords'], etc.
        updated_info = service_fn(**inputs)
        
        # 4) Persist immediately back to disk
        path = get_video_info_path(**info_data)
        safe_dump_to_file(data=updated_info, file_path=path)

        return updated_info
