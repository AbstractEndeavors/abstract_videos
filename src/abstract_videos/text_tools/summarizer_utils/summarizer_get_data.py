from .summarizer_services import get_summary
from ...whisper_utils import get_whisper_text_data
from ..keybert_utils.keybert_calls import get_keybert_list
def get_summary_data(info_data=None,**kwargs):
    full_text = get_whisper_text_data(info_data=info_data)
    keywords = get_keybert_list(**info_data)
    result = get_summary(keywords=keywords,
                         full_text=full_text)
    return result
def get_summary_info_data(info_data=None,**kwargs):
    info_data = info_data or {}
    result = get_summary_data(info_data=info_data,**kwargs)
    info_data['summary'] = result
    return info_data
