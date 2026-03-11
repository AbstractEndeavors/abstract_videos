from .keybert_services import refine_keywords
from ...audio_tools.whisper_utils import get_whisper_text
def get_keywords_data(info_data=None,**kwargs):
    full_text = get_whisper_text(**kwargs)
    keywords = get_keywords_list(**kwargs)
    keywords,combined_keywords,keyword_density = refine_keywords(
        keywords=keywords,
        full_text=full_text)
    return keywords,combined_keywords,keyword_density
def get_keywords_info_data(info_data=None,**kwargs):
    info_data = info_data or {}
    keywords,combined_keywords,keyword_density = get_keywords_data(info_data=info_data,**kwargs)
    info_data['keywords'] = keywords
    info_data['combined_keywords'] = combined_keywords
    info_data['keyword_density'] = keyword_density
    return info_data
