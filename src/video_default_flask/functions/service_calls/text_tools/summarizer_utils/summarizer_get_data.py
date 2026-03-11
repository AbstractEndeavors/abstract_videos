from .summarizer_services import get_summary
from ...audio_tools.whisper_utils import get_whisper_text
from ..keybert_utils.keybert_calls import get_keybert_list
def get_summary_data(info_data=None,**kwargs):
    full_text = get_whisper_text(**kwargs)
    keywords = get_keybert_list(**kwargs)
    result = get_summary(keywords=keywords,
                         full_text=full_text)
    return result
def get_summary_info_data(info_data=None,**kwargs):
    info_data = info_data or {}
    result = get_summary_data(info_data=info_data,**kwargs)
    info_data['summary'] = result
    return info_data
