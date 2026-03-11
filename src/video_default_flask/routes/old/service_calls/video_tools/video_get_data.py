from .video_services import analyze_video_text
from .routes import *
def get_analyze_video_text(info_data=None,**kwargs):
    result = analyze_video_text(video_path=info_data.get('video_path'),
        directory=info_data.get('thumbnails_directory'),
        image_texts=info_data.get('video_text',[]),
        remove_phrases=info_data.get('remove_phrases',[]),
        video_id=info_data.get('video_id'),
        frame_interval=info_data.get('frame_interval'))
    return result
def get_analyze_video_text_data(info_data=None,**kwargs):
    info_data = info_data or {}
    new_data = {}
    new_data['video_text'] = get_analyze_video_text(info_data=None,**kwargs)
    info_data = update_json_data(info_data,new_data,keys=True)
    return info_data
