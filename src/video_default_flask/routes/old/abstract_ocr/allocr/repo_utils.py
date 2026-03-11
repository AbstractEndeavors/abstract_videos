from .functions import update_json_data,execute_if_bool,generate_file_id
from .variable_utils import *
from .video_utils import extract_audio_from_video,analyze_video_text
from .audio_utils import transcribe_with_whisper_local
from .text_utils import refine_keywords,get_summary
from .seo_utils import get_seo_data

def get_summary_data(info_data=None,**kwargs):
    info_data = info_data or {}
    result = get_summary(keywords=info_data.get('keywords'),
        full_text=info_data.get('full_text'))
    info_data['summary'] = result
    return info_data
def get_transcribe_with_whisper_local_data(info_data=None,**kwargs):
    info_data = info_data or {}
    result = transcribe_with_whisper_local(
        audio_path=info_data.get('audio_path'),
        model_size=info_data.get('model_size',"tiny"),
        use_silence=info_data.get('use_silence'),
        info_data=info_data.get('info_data'))
    get_recieve_whisper_data(result,**info_data)
    return info_data
def get_analyza_video_text_data(info_data=None,**kwargs):
    info_data = info_data or {}
    result = analyze_video_text(video_path=info_data.get('video_path'),
        directory=info_data.get('thumbnails_directory'),
        image_texts=info_data.get('video_text',[]),
        remove_phrases=info_data.get('remove_phrases',[]),
        video_id=info_data.get('video_id'),
        frame_interval=info_data.get('frame_interval'))
    info_data['video_text'] = result
    return info_data
