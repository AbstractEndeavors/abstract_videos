from ..service_calls import (execute_whisper_transcription_call,
                                         get_keyword_execution_variables,
                                         execute_video_text_variables,
                                         get_summary_execution_variables)
from .bool_utils import execute_if_bool
from moviepy.editor import *
import moviepy.editor as mp
from .functions import get_key_vars
def extract_audio_from_video(video_path, audio_path):
    """Extract audio from a video file using moviepy."""
    try:
        logger.info(f"Extracting audio from {video_path} to {audio_path}")
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        video.close()
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file {audio_path} was not created.")
        logger.info(f"Audio extracted successfully: {audio_path}")
        return audio_path
    except Exception as e:
        logger.error(f"Error extracting audio from {video_path}: {e}")
        return None
    
def execute_whisper_call(req=None,info_data=None):
    return execute_whisper_transcription_call(req=req,info_data=info_data)
def execute_keywords_call(req=None,info_data=None):
    keys,function,bool_key = get_keyword_execution_variables(req=req,info_data=info_data)
    info_data = execute_if_bool(bool_key,function,keys,req=req,info_data=info_data)
    return info_data
def execute_video_text_call(req=None,info_data=None):
    return execute_video_text_variables(req=req,info_data=info_data)

    keys,function,bool_key = get_summary_execution_variables(req=req,info_data=info_data)
    info_data = execute_if_bool(bool_key,function,keys,req=req,info_data=info_data)
def execute_summarizer_call(req=None,info_data=None):
    keys,function,bool_key = get_summary_execution_variables(req=req,info_data=info_data)
    info_data = execute_if_bool(bool_key,function,keys,req=req,info_data=info_data)
    return info_data

def extract_audio_from_video_call(req=None,info_data=None):
   new_data,info_data = get_key_vars(['audio_path','video_path'],req,info_data)
   audio_path = new_data.get('audio_path')
   video_path = new_data.get('video_path')
   if audio_path and video_path and not os.path.isfile(audio_path):
        
        extract_audio_from_video(audio_path=audio_path,video_path=video_path)
   return info_data
def get_initial_info_data(**kwargs):
    # 1) Populate all the “core” fields (paths, IDs, etc.)
    keys = [
        'video_path', 'basename', 'filename', 'ext', 'title',
        'video_id', 'info_directory', 'info_path', 'parent_directory',
        'audio_path', 'thumbnails_directory',
        'uploader', 'domain', 'videos_url', 'canonical_url',
        'remove_phrases', 'categories', 'repository_dir',
        'directory_links', 'videos_dir', 'infos_dir',
        'base_url', 'model_size', 'language',
    ]
    # pull existing metadata from disk (if any)
    info_data = get_video_info_data(**kwargs) or {}
    new_data, info_data = get_key_vars(keys, data=info_data, info_data=info_data)

    vp = new_data['video_path']
    ap = new_data['audio_path']
    td = new_data['thumbnails_directory']

    # 2) Ensure audio exists
    if vp and ap and not os.path.isfile(ap):
        result = extract_audio_from_video(video_path=vp, audio_path=ap)
        if result:
            info_data['audio_path'] = ap

    # 3) Ensure at least one thumbnail exists
    #    (you’ll need to write your own create_thumbnails helper)
    if vp and td and not any(os.scandir(td)):
        thumbs = create_thumbnails(video_path=vp, output_dir=td)
        # e.g. create_thumbnails returns a list of file‐paths
        info_data['thumbnails'] = thumbs

    # 4) Persist your updates back into info.json
    safe_save_updated_json_data(
        data={'audio_path': info_data.get('audio_path'),
              'thumbnails': info_data.get('thumbnails', [])},
        file_path=get_video_info_path(**info_data),
        valid_keys=['audio_path', 'thumbnails'],
        invalid_keys=[]
    )
    info_data = execute_whisper_transcription_call(info_data=info_data)
    keys,function,bool_key = get_keyword_execution_variables(info_data=info_data)
    info_data = execute_if_bool(bool_key,function,keys,req=None,info_data=info_data)
    info_data = execute_video_text_variables(req=None,info_data=info_data)
    keys,function,bool_key = get_summary_execution_variables(req=None,info_data=info_data)
    info_data = execute_if_bool(bool_key,function,keys,req=None,info_data=info_data)
    return info_data
