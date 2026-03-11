
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
