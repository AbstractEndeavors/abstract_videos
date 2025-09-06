from .whisper_services import transcribe_with_whisper_local
#from .whisper_calls import get_recieve_whisper_data
def get_whisper_data(info_data=None):
    info_data = info_data or {}
    whisper_result_path = info_data.get('whisper_result_path')
    if os.path.isfile(whisper_result_path):
        return safe_read_from_json(whisper_result_path)
def get_whisper_text_data(info_data=None):
    info_data = info_data or {}
    whisper_text = info_data.get('text')
    return whisper_text
def get_whisper_segments_data(info_data=None):
    whisper_data = get_whisper_data(info_data) or {}
    whisper_segments = whisper_data.get('segments')
    return whisper_segments
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
def get_transcribe_with_whisper_local_data(info_data=None,**kwargs):
    new_data,info_data = get_whisper_key_vars(info_data=info_data)
    result = transcribe_with_whisper_local(**new_data)
    return result,info_data
def get_transcribe_with_whisper_local_info_data(info_data=None,**kwargs):
    info_data = info_data or {}
    result,info_data = get_transcribe_with_whisper_local_data(info_data=info_data,**kwargs)
    get_recieve_whisper_data(result,**info_data)
    return info_data
