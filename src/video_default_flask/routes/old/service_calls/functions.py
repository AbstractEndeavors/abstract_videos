import re,math,spacy,pytesseract,cv2,PyPDF2,argparse,whisper,shutil,os,sys,json,logging,glob,hashlib
from datetime import datetime
from  datetime import timedelta 
from PIL import Image
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
import speech_recognition as sr
from pydub.silence import detect_nonsilent
from pydub.silence import split_on_silence
from pydub import AudioSegment
from abstract_math import (divide_it,
                           multiply_it)
from typing import *
from urllib.parse import quote
import moviepy.editor as mp
from moviepy.editor import *
import math
import os
import whisper
from pydub import AudioSegment
from pydub.silence import split_on_silence

def get_result_path(pathname, info_data=None, **kwargs):
    # merge either top-level kwargs or the nested dict
    data = {**(info_data or {}), **kwargs}
    info_dir = get_video_info_dir(**data)
    return os.path.join(info_dir, pathname)
def get_whisper_result_data(**kwargs):
    return WhisperPipeline(kwargs).run()

def get_whisper_text(**kwargs):
    # still called get_whisper_text, but now driven by the pipeline
    data = get_whisper_result_data(**kwargs)
    return get_result_from_data("text", lambda **k: data, **kwargs)

def get_whisper_segment(**kwargs):
    data = get_whisper_result_data(**kwargs)
    return get_result_from_data("segments", lambda **k: data, **kwargs)

def get_recieve_whisper_data(data, **kwargs):
    # you likely won’t need this anymore, pipeline.save() covers it
    return safe_save_updated_json_data(
        data,
        WhisperPipeline(kwargs)._result_path(),
        valid_keys=VALID_KEYS,
        invalid_keys=INVALID_KEYS,
    )

def is_whisper_data(**info_data):
    return WhisperPipeline(info_data).exists()
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


class WhisperPipeline:
    def __init__(self, new_data: dict, parent_info=None):
        # if parent_info was None, default it:
        self.new_data = new_data
        parent_info = parent_info or {}
        # combine them so both sets of keys live together
        self.info = {**parent_info, **new_data}
        
        # now this will never be None
        self.directory = (
            self.info.get('info_dir')
            or self.info.get('info_directory')
            or os.path.dirname(self.info.get('info_path', ''))
        )
        self.audio_path = self.info.get('audio_path')
        self.model_size = self.info.get('model_size',"tiny")
        self.language = self.info.get('language',"english")
        self.use_silence = self.info.get('use_silence',"True")
        self.video_id = self.info.get('video_id') or os.path.basename(self.directory)
        self.file_path = os.path.join(self.directory, 'whisper_result.json')
    def _result_path(self) -> str:
        
        return self.file_path

    def load(self) -> dict | None:
        return safe_read_from_json(self.file_path)

    def exists(self) -> bool:
        return os.path.isfile(self.file_path)

    def transcribe(self) -> dict:
        self.transcript_data = transcribe_with_whisper_local(audio_path=self.audio_path,
                                                             model_size=self.model_size,
                                                             language=self.language,
                                                             use_silence=self.use_silence)
        return self.transcript_data

    def save(self, result: dict):
        safe_save_updated_json_data(
            self.transcript_data,
            self.file_path,
            valid_keys=VALID_KEYS,
            invalid_keys=INVALID_KEYS,
        )

    def export_srt(self, output_path: str | None = None):
        data = safe_load_from_json(self.file_path)
        export_srt_whisper(data, output_path or self.directory)

    def run(self) -> dict:
        self.info = update_json_data(self.info, self.info, keys=True)
        if not self.exists():
            self.transcript_data = self.transcribe()
            safe_dump_to_json(data=self.transcript_data,file_path=self.file_path)
        self.info = update_json_data(self.info, self.info, keys=True)
        return self.info
    
def execute_whisper_transcription_call(req=None, info_data=None):
    # 1) pull out the whisper inputs (audio_path, model_size, etc.)
    new_data, info_data = get_whisper_key_vars(req=req, info_data=info_data)  # :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}

    # 2) decide if we need to run (same as your bool-utils approach)
    should_run, info_data = get_whisper_bool_key(req=req, info_data=info_data)  # :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}
    if should_run:
        # 3) run the pipeline, which returns {'text':…, 'segments':…}
        pipeline = WhisperPipeline(new_data, info_data) 
        info = pipeline.run()
        info_data = update_json_data(info_data, info, keys=True)
        # 4) merge the result back into info_data
    info_data = update_json_data(info_data, new_data, keys=True)
    logger.info(f" for execute_video_text_variables ||| THIS IS THE GODDAMN INF FUCKING DATA{info_data}")
    return info_data
from abstract_utilities import (timestamp_to_milliseconds,
                                format_timestamp,
                                get_time_now_iso,
                                parse_timestamp,
                                get_logFile,
                                make_dirs,
                                safe_dump_to_file,
                                safe_read_from_json,
                                read_from_file,
                                write_to_file,
                                path_join,
                                confirm_type,
                                get_media_types,
                                get_all_file_types,
                                eatInner,
                                eatOuter,
                                eatAll,
                                get_all_file_types,
                                is_media_type,
                                safe_load_from_json,)
                                
from abstract_utilities.json_utils import safe_update_json_datas,safe_save_updated_json_data
def get_info_data_from_data(data):
    info_data = data.get('json_data',{}) or data.get('info_data',{}) or data.get('data',{}) or data.get('info',{})
    return info_data
def get_request_info_data(req):
    data = get_request_data(req)
    info_data = get_info_data_from_data(data)
    data = update_json_data(data,info_data)
    info_data = update_json_data(info_data,data,keys=True)
    return data,info_data
from keybert import KeyBERT
from transformers import pipeline
import torch,os,json,unicodedata,hashlib
from transformers import LEDTokenizer,LEDForConditionalGeneration
from abstract_flask import get_request_data
summarizer = pipeline("summarization", model="Falconsai/text_summarization")
keyword_extractor = pipeline("feature-extraction", model="distilbert-base-uncased")
generator = pipeline('text-generation', model='distilgpt2', device= -1)
kw_model = KeyBERT(model=keyword_extractor.model)                           
logger = get_logFile('vid_to_aud')
logger.debug(f"Logger initialized with {len(logger.handlers)} handlers: {[h.__class__.__name__ for h in logger.handlers]}")

logOn=True
DOMAIN='https://typicallyoutliers.com'
UPLOADER='The Daily Dialectics'
MAIN_DIR = "/var/www/typicallyoutliers"
FRONTEND_DIR = f"{MAIN_DIR}/frontend"
CATEGORIES = {}
SRC_DIR = f"{FRONTEND_DIR}/src"
BUILD_DIR = f"{FRONTEND_DIR}/build"
PUBLIC_DIR = f"{FRONTEND_DIR}/public"

STATIC_DIR = f"{BUILD_DIR}/static"

IMGS_URL = f"{DOMAIN}/imgs"
IMGS_DIR = f"{PUBLIC_DIR}/imgs"

REPO_DIR = f"{PUBLIC_DIR}/repository"
VIDEOS_URL = f"{DOMAIN}/videos"
VIDEOS_DIR = f"{REPO_DIR}/videos"
VIDEO_DIR = f"{REPO_DIR}/Video"
TEXT_DIR = f"{REPO_DIR}/text_dir"

VIDEO_OUTPUT_DIR = TEXT_DIR
DIR_LINKS = {TEXT_DIR:'infos',VIDEOS_DIR:'videos',REPO_DIR:'repository',IMGS_DIR:'imgs'}
REMOVE_PHRASES = ['Video Converter', 'eeso', 'Auseesott', 'Aeseesott', 'esoft']
DOMAIN='https://typicallyoutliers.com'
UPLOADER='The Daily Dialectics'
VIDEO_OUTPUT_DIR = TEXT_DIR
DIR_LINKS = {TEXT_DIR:'infos',VIDEOS_DIR:'videos',REPO_DIR:'repository',IMGS_DIR:'imgs'}
REMOVE_PHRASES = ['Video Converter', 'eeso', 'Auseesott', 'Aeseesott', 'esoft']
DOMAIN='https://typicallyoutliers.com'
UPLOADER='The Daily Dialectics'
VALID_KEYS =     ['parent_dir', 'video_path', 'info_dir','info_directory',
                  'thumbnails_directory', 'info_path',
                  'filename', 'ext', 'remove_phrases',
                  'audio_path', 'video_json', 'categories',
                  'uploader','domain', 'videos_url', 'video_id',
                  'canonical_url', 'chunk_length_ms',
                  'chunk_length_diff',
                  'renew', 'whisper_result', 'video_text',
                  'keywords', 'combined_keywords', 'keyword_density',
                  'summary', 'seo_title', 'seo_description',
                  'seo_tags', 'thumbnail', 'duration_seconds',
                  'duration_formatted', 'captions_path',
                  'schema_markup', 'social_metadata', 'category',
                  'publication_date', 'file_metadata']
INVALID_KEYS = ['LEDForConditionalGeneration','LEDTokenizer','generator','info_data','json_data','full_text','whisper_result']
def create_key_value(json_obj, key, value):
    json_obj[key] = json_obj.get(key, value) or value
    return json_obj

def getPercent(i):
    return divide_it(i, 100)

def getPercentage(num, i):
    percent = getPercent(i)
    percentage = multiply_it(num, percent)
    return percentage

def if_none_get_def(value, default):
    if value is None:
        value = default
    return value

def if_not_dir_return_None(directory):
    str_directory = str(directory)
    if os.path.isdir(str_directory):
        return str_directory
    return None

def determine_remove_text(text,remove_phrases=None):
    remove_phrases=remove_phrases or []
    found = False
    for remove_phrase in remove_phrases:
        if remove_phrase in text:
            found = True
            break
    if found == False:
        return text

def generate_file_id(path: str, max_length: int = 50) -> str:
    base = os.path.splitext(os.path.basename(path))[0]
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode('ascii')
    base = base.lower()
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    base = re.sub(r'-{2,}', '-', base)
    if len(base) > max_length:
        h = hashlib.sha1(base.encode()).hexdigest()[:8]
        base = base[: max_length - len(h) - 1].rstrip('-') + '-' + h
    return base
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s:.,-]', '', text)
    text = text.strip()
    return text
def get_frame_number(file_path):
    file_path = '.'.join(file_path.split('.')[:-1])
    return int(file_path.split('_')[-1])
def sort_frames(frames=None,directory=None):
    if frames in [None,[]] and directory and os.path.isdir(directory):
        frames = get_all_file_types(types=['image'],directory=directory)
    frames = frames or []
    frames = sorted(
        frames,
        key=lambda x: get_frame_number(x) 
    )
    return frames
    
def get_from_list(list_obj=None,length=1):
    list_obj = list_obj or []
    if len(list_obj) >= length:
        list_obj = list_obj[:length]
    return list_obj
def get_image_metadata(file_path):
    """Extract image metadata (dimensions, file size)."""
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            file_size = get_file_size(file_path)
        return {
            "dimensions": {"width": width, "height": height},
            "file_size": round(file_size, 3)
        }
    except Exception as e:
        return {"dimensions": {"width": 0, "height": 0}, "file_size": 0}
from collections.abc import Mapping
from typing import Any, Dict, Sequence, Optional

def safe_update_json_datas(
    json_data: Dict[str, Any],
    update_data: Any,
    valid_keys:        Optional[Sequence[str]] = None,
    invalid_keys:      Optional[Sequence[str]] = None
) -> Dict[str, Any]:
    """
    Return a new dict merging json_data with update_data:
      • Drops any keys in invalid_keys
      • Keeps only keys in valid_keys (if provided) from update_data
      • Otherwise merges all of update_data
    Raises TypeError if update_data isn’t a mapping.
    """
    if not isinstance(update_data, Mapping):
        print(update_data)
        print(f"update_data must be a mapping, got {type(update_data).__name__}")
    else:
        # 1) drop blacklisted keys from the original
        invalid = set(invalid_keys or ())
        base = {k: v for k, v in json_data.items() if k not in invalid}

        # 2) choose which updates to apply
        valid = set(valid_keys or ())
        if valid:
            updates = {k: update_data[k] for k in valid if k in update_data}
        else:
            updates = dict(update_data)

        # 3) shallow merge (updates win)
        return {**base, **updates}


def update_json_data(
    json_data: Dict[str, Any],
    update_data: Any,
    keys: bool = False
) -> Dict[str, Any]:
    """
    Wrapper: optionally uses VALID_KEYS/INVALID_KEYS,
    and will raise if update_data isn't dict-like.
    """
    if not isinstance(update_data, dict):
        raise TypeError(f"update_data must be a dict, got {type(update_data).__name__}")

    vk, ik = (VALID_KEYS, INVALID_KEYS) if keys else (None, None)
    return safe_update_json_datas(json_data, update_data, valid_keys=vk, invalid_keys=ik)


def update_sitemap(video_data,
                   sitemap_path):
    with open(sitemap_path, 'a') as f:
        f.write(f"""
<url>
    <loc>{video_data['canonical_url']}</loc>
    <video:video>
        <video:title>{video_data['seo_title']}</video:title>
        <video:description>{video_data['seo_description']}</video:description>
        <video:thumbnail_loc>{video_data['thumbnail']['file_path']}</video:thumbnail_loc>
        <video:content_loc>{video_data['video_path']}</video:content_loc>
    </video:video>
</url>
""")
def _format_srt_timestamp(seconds: float) -> str:
    """
    Convert seconds (e.g. 3.2) into SRT timestamp "HH:MM:SS,mmm"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - math.floor(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
def execute_if_bool(bool_key,function,keys,req=None,info_data=None):
    new_data,info_data = get_key_vars(keys,req,info_data)
    bool_response = bool_key
    if not isinstance(bool_response,bool):
        bool_response = info_data.get(bool_key) in [None,'',[],"",{}]
    logger.info(f"{bool_key} == {bool_response}")
    if bool_response:
        info = function(**new_data)
        print(info)
        print(bool_key)
        info_data = update_json_data(info_data,info,keys=True)
    safe_dump_to_file(data=info_data,file_path=get_video_info_path(**info_data))
    return info_data
def generate_file_id(path: str, max_length: int = 50) -> str:
    base = os.path.splitext(os.path.basename(path))[0]
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode('ascii')
    base = base.lower()
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    base = re.sub(r'-{2,}', '-', base)
    if len(base) > max_length:
        h = hashlib.sha1(base.encode()).hexdigest()[:8]
        base = base[: max_length - len(h) - 1].rstrip('-') + '-' + h
    return base
def get_video_id(**kwargs):
    info_data = kwargs.get('info_data',kwargs)
    info_dir = info_data.get('info_dir') or info_data.get('info_directory')
    video_id = info_data.get('video_id')
    video_path = info_data.get('video_path')
    if info_dir:
        video_id = os.path.basename(info_dir)
    if video_path:
        video_id = generate_file_id(video_path)
    if video_id:
        return video_id
def get_videos_path(directory = None, info_data = None):
    info_data = info_data or {}
    if info_data and directory == None:
        directory = info_data['output_dir']
    directory = directory or TEXT_DIR
    return directory
def get_video_basenames(directory = None, info_data = None):
    directory = get_videos_path(directory = None, info_data = None)
    directory_items = os.listdir(directory)
    return directory_items

def get_videos_paths(directory = None, info_data = None):
    directory = get_videos_path(directory = directory, info_data = info_data)
    video_basenames = get_video_basenames(directory = directory, info_data = directory)
    directory_items = [os.path.join(directory,basename) for basename in video_basenames]
    return directory_items

def get_videos_infos(directory = None, info_data = None):
    directory_items = get_videos_paths(directory = directory, info_data = info_data)
    directory_infos = [get_video_info_data(item_path) for item_path in directory_items]
    return directory_infos

def get_thumbnails_dir(info_dir=None,**kwargs):
    video_info_dir = info_dir or get_video_info_dir(**kwargs)
    thumbnails_directory=os.path.join(video_info_dir,'thumbnails')
    os.makedirs(thumbnails_directory,exist_ok=True)
    return thumbnails_directory

def get_video_info_dir(**kwargs):
    video_id = get_video_id(**kwargs)
    info_dir = os.path.join(TEXT_DIR,video_id)
    
    os.makedirs(info_dir,exist_ok=True)
    get_thumbnails_dir(info_dir)
    return info_dir

def get_video_info_path(**kwargs):
    info_dir = get_video_info_dir(**kwargs)
    info_path = os.path.join(info_dir,'info.json')
    return info_path

def get_whisper_result_path(**kwargs):
    info_dir = get_video_info_dir(**kwargs)
    info_path = os.path.join(info_dir,'whisper_result.json')
    return info_path

def get_whisper_result_data(**kwargs):
    whisper_result_path = get_whisper_result_path(**kwargs)
    whisper_result_data=None
    if os.path.isfile(whisper_result_path):
        whisper_result_data = safe_load_from_json(whisper_result_path)
    return whisper_result_data

def get_whisper_text(**kwargs):
    whisper_result_data = get_whisper_result_data(**kwargs)
    whisper_text = whisper_result_data.get('text')
    return whisper_text

def get_whisper_segment(**kwargs):
    whisper_result_data = get_whisper_result_data(**kwargs)
    whisper_text = whisper_result_data.get('segment')
    return whisper_text

def get_recieve_whisper_data(data,**kwargs):
    whisper_result_path = get_whisper_result_path(**kwargs)
    if not os.path.exists(whisper_result_path):
        safe_dump_to_file(data={},file_path=whisper_result_path)
    whisper_data = safe_read_from_json(whisper_result_path)
    whisper_data = update_json_data(whisper_data,data)
    safe_dump_to_file(data=whisper_data, file_path=whisper_result_path)
def def_dump_info_data(info_data,**kwargs):    
    whisper_response =info_data.get('whisper_response')
    if whisper_response:
        get_recieve_whisper_data(whisper_response,**kwargs)
        
def get_video_info_data(**kwargs):
    info_data=kwargs.get('info_data',kwargs) or kwargs  or {}
    info_file_path = None
    if info_data and isinstance(info_data,str) and os.path.isdir(info_data):
        info_dir = info_data
        info_file_path = os.path.join(info_dir,'info.json')
    elif info_data and isinstance(info_data,str) and os.path.isfile(info_data):
        info_file_path = info_data
    else:
        info_file_path = get_video_info_path(**info_data)
    if os.path.isfile(info_file_path):
        info_data = safe_load_from_json(info_file_path)
        return info_data

def get_audio_path(**kwargs):
    info_dir = get_video_info_dir(**kwargs)
    audio_path = os.path.join(info_dir,'audio.wav')
    return audio_path

def get_audio_bool(**kwargs):
    audio_path = get_audio_path(**kwargs)
    if audio_path:  
        return os.path.isfile(audio_path)
    return False
def get_video_basename(**kwargs):
    video_path = kwargs.get('video_path')
    if not video_path:
        info_data = get_video_info_data(**kwargs)
        video_path = info_data.get('video_path')
    if video_path:
        basename= os.path.basename(video_path)
        return basename
def get_video_filename(**kwargs):
    basename = get_video_basename(**kwargs)
    filename,ext = os.path.splitext(basename)
    return filename
def get_video_ext(**kwargs):
    basename = get_video_basename(**kwargs)
    filename,ext = os.path.splitext(basename)
    return ext
def get_canonical_url(**kwargs):
    video_id = get_video_id(**kwargs)
    videos_url = kwargs.get('videos_url') or kwargs.get('video_url') or VIDEO_URL
    canonical_url = f"{videos_url}/{video_id}"
    return canonical_url
def get_key_vars(keys,req=None,data=None,info_data= None):
    new_data = {}
    if req:
        data,info_data = get_request_info_data(req)
    info_data = info_data or {}
    data = data or info_data
    all_data = data
    for key in keys:
        new_data[key] = all_data.get(key)
        if not new_data[key]:
            if key == 'audio_path':
                new_data[key] = get_audio_path(**all_data)
            elif key == 'video_path':
                new_data[key] = all_data.get('video_path')
            elif key == 'basename':
                new_data[key] = get_video_basename(**all_data)
            elif key == 'filename':
                new_data[key] = get_video_filename(**all_data)
            elif key == 'ext':
                new_data[key] = get_video_ext(**all_data)
            elif key == 'title':
                new_data[key] = get_video_filename(**all_data)
            elif key == 'video_id':
                new_data[key] = get_video_id(**all_data)
            elif key == 'video_path':
                new_data[key] = get_video_path(**all_data)
            elif key == 'thumbnails_directory':
                new_data[key] = get_thumbnails_dir(**all_data)
            elif key == 'model_size':
               new_data[key] = "tiny"
            elif key == 'use_silence':
               new_data[key] = True
            elif key == 'language':
               new_data[key] = "english"
            elif key == 'remove_phrases':
                new_data[key] = REMOVE_PHRASES
            elif key == 'uploader':
                new_data[key] = UPLOADER
            elif key == 'domain':
                new_data[key] = DOMAIN
            elif key == 'categories':
                new_data[key] = CATEGORIES
            elif key == 'videos_url':
                new_data[key] = VIDEOS_URL
            elif key == 'repository_dir':
                new_data[key] = REPO_DIR
            elif key == 'directory_links':
                new_data[key] = DIR_LINKS
            elif key == 'videos_dir':
                new_data[key] = VIDEOS_DIR
            elif key == 'infos_dir':
                new_data[key] = IMGS_DIR
            elif key == 'info_path':
                new_data[key] = get_video_info_path(**all_data)
            elif key in ['info_dir','info_directory']:
                new_data[key] = get_video_info_dir(**all_data)
            elif key == 'base_url':
                new_data[key] = DOMAIN
            elif key == 'generator':
                new_data[key] = generator
            elif key == 'LEDTokenizer':
                new_data[key] = LEDTokenizer
            elif key == 'LEDForConditionalGeneration':
                new_data[key] = LEDForConditionalGeneration
            elif key == 'full_text':
                new_data[key] = get_whisper_text(**all_data)
            elif key == 'parent_directory':
                new_data[key] = TEXT_DIR
        all_data = update_json_data(all_data,new_data)
    info_data = update_json_data(info_data,all_data,keys=True)
    if 'info_data' in keys:
        new_data['info_data'] =info_data
    if 'json_data' in keys:
        new_data['json_data'] =info_data
    return new_data,info_data

def split_infos(**kwargs):
    video_id = get_video_id(**kwargs)
    info_directory = make_dirs(TEXT_DIR, video_id)
    info_path = os.path.join(info_directory, 'info.json')
    info = safe_read_from_json(info_path)
    whisper_result = info.get('whisper_result')
    if whisper_result:
        whisper_result_path = os.path.join(info_directory, 'whisper_result.json')
        safe_dump_to_file(data=whisper_result, file_path=info_path)
        del info['whisper_result']
        safe_dump_to_file(data=info, file_path=whisper_result_path)
    info = safe_read_from_json(info_path)
    return info
def rename(**kwargs):
    video_id = get_video_id(**kwargs)
    info_directory = os.path.joinb(TEXT_DIR, video_id)
    info_path = os.path.join(info_directory, 'info.json')
    info = safe_read_from_json(info_path)
    video_path = kwargs.get('video_path')
    segments_result = info.get('segments')
    text_result = info.get('text')
    language_result = info.get('language')
    all_whisper = True
    for key,value in info.items():
        if key not in ['language','text','segments']:
            all_whisper = False
            break
    whisper_result_path = os.path.join(info_directory, 'whisper_result.json')
    if all_whisper:
        if os.path.isdir(whisper_result_path):
            shutil.rmtree(whisper_result_path)
        if os.path.isfile(info_path):
            shutil.move(info_path,whisper_result_path)
    get_all_info_data_call(video_path,info_dir=info_directory)    
    safe_dump_to_file(data=whisper_result, file_path=info_path)
    info = safe_read_from_json(info_path)
    return info
EXT_TO_PREFIX = {
    **dict.fromkeys(
        {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'},
        'infos'
    ),
    **dict.fromkeys(
        {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'},
        'videos'
    ),
    '.pdf': 'pdfs',
    **dict.fromkeys({'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}, 'audios'),
    **dict.fromkeys({'.doc', '.docx', '.txt', '.rtf'}, 'docs'),
    **dict.fromkeys({'.ppt', '.pptx'}, 'slides'),
    **dict.fromkeys({'.xls', '.xlsx', '.csv'}, 'sheets'),
    **dict.fromkeys({'.srt'}, 'srts'),
}

def get_seo_data_call(req=None,info_data=None):
    keys = ['uploader',
            'domain',
            'categories',
            'videos_url',
            'repository_dir',
            'directory_links',
            'videos_dir',
            'infos_dir',
            'base_url',
            'generator',
            'LEDTokenizer',
            'LEDForConditionalGeneration',
            'info_data']
    bool_key = 'seo_description'
    function = get_seo_data
    info_data = execute_if_bool(bool_key,function,keys,info_data=info_data)
    return info_data


