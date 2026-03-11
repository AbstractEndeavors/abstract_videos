from .routes import *
def is_video_text_data(**info_data):
    bool_key = info_data.get('video_text') == None
    return bool_key
