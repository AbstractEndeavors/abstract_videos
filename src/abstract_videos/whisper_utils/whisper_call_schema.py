from .routes import *
from .whisper_calls import *
from .whisper_get_data import *
# in your routes (or wherever execute_whisper_call lives)
from .whisper_pipeline import WhisperPipeline

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

def get_whisper_execution_variables(req=None, info_data=None):
    # 1) pull out the whisper inputs (audio_path, model_size, etc.)
    new_data, info_data = get_whisper_key_vars(req=req, info_data=info_data)  # :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}

    # 2) decide if we need to run (same as your bool-utils approach)
    should_run, info_data = get_whisper_bool_key(req=req, info_data=info_data)  # :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}
    if should_run:
        # 3) run the pipeline, which returns {'text':…, 'segments':…}
        pipeline = WhisperPipeline(new_data)                                # :contentReference[oaicite:4]{index=4}&#8203;:contentReference[oaicite:5]{index=5}
        result = pipeline.run()

        # 4) merge the result back into info_data
        info_data.update(result)

    return info_data
