import os,re,unicodedata,hashlib,math,os,ffmpeg
import os
from abstract_apis import *
from functools import lru_cache
from video_utils import *
from random import randrange
from PIL import Image
from datetime import datetime
from abstract_math import divide_it
from abstract_utilities import safe_read_from_json,is_number,get_logFile,make_dirs
from typing import *
from abstract_ocr import *
from keybert import KeyBERT
from transformers import pipeline
import torch,os,json
from transformers import LEDTokenizer,LEDForConditionalGeneration
summarizer = pipeline("summarization", model="Falconsai/text_summarization")
keyword_extractor = pipeline("feature-extraction", model="distilbert-base-uncased")
generator = pipeline('text-generation', model='distilgpt2', device= -1)
kw_model = KeyBERT(model=keyword_extractor.model)
logger = get_logFile('video_utils')
BASE_URL = "https://typicallyoutliers.com"
TEXT_DIR = '/var/www/typicallyoutliers/frontend/public/repository/text_dir/'
VIDEO_DIR = '/var/www/typicallyoutliers/frontend/public/repository/Video/'
REPO_DIR = '/var/www/typicallyoutliers/frontend/public/repository'
IMGS_DIR = '/var/www/typicallyoutliers/frontend/public/imgs'
DIR_LINKS = {TEXT_DIR:'infos',VIDEO_DIR:'videos',REPO_DIR:'repository',IMGS_DIR:'imgs'}
def get_audio_file(video_id=None,info_data=None):
    video_path = get_video_path(video_id=video_id,info_data=info_data)
    audio_path = extract_audio_from_video(video_path,audio_path)
    info_data = transcribe_with_whisper_local(
                                json_data=info_data,
                                audio_path=audio_path,
                                model_size="medium",           # one of "tiny", "base", "small", "medium", "large"
                                language='english')
    return info_data     
class videoPathManager:
    def __init__(self):
        self.video_paths = []
        self.video_ids = os.listdir(TEXT_DIR)
        self.video_directories = self.get_all_video_paths()
    def get_all_video_paths(self):
        video_directories = {video_id:{"directory":make_dirs(TEXT_DIR,video_id)} for video_id in self.video_ids}
        for directory in video_directories:
            video_id = os.path.basename(directory)
            info_path = get_info_path(video_id=video_id)
            info_data = safe_read_from_json(info_path) or {}
            video_directories[video_id]['video_path'] = info_data.get('video_path')
        return video_directories
    def get_video_path(self,video_id):
        return video_directories[video_id]['video_path']
    def get_video_id(self,video_path):
        for video_id,values in self.video_directories.items():
            if video_path == values.get('video_path'):
                return video_id
        video_id = generate_video_id(video_path)
        self.video_ids.append(video_id)
        self.add_path(video_id,video_path)
        return video_id
    def get_info_data(self,video_path=None,video_id=None):
        video_path = video_path or self.get_video_path(video_id)
        if video_path:
            info_data = self.video_directories[video_id]
            info_data['video_id'] = video_id
            info_data['directory'] = make_dirs(TEXT_DIR,info_data['video_id'])
            info_data['info_path'] = os.path.join(info_data['directory'],'info.json')
            info_data['video_path'] = video_path
            return info_data
    def add_path(self,video_id,video_path):
        if self.video_directories.get(video_id) == None:
            self.video_directories[video_id] = {}
        self.video_directories[video_id]['video_path'] = video_path
        self.video_directories[video_id]["directory"] = make_dirs(TEXT_DIR,video_id)
        directory = make_dirs(self.video_directories[video_id]["directory"])
        info_path = os.path.join(directory,'info.json')
        info_data = self.video_directories[video_id]
        info_data['video_id'] = video_id
        safe_dump_to_file(info_data,info_path)
        return info_data

def find_tex_file(file_path):
    basename = os.path.basename(file_path)
    filename,ext = os.path.splitext(basename)
    text_dir_items = os.listdir(TEXT_DIR)
    if basename in text_dir_items:
        input(basename)
def generate_video_id(path: str, max_length: int = 50) -> str:
    # 1. Take basename (no extension)
    base = os.path.splitext(os.path.basename(path))[0]
    # 2. Normalize Unicode → ASCII
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode('ascii')
    # 3. Lower-case
    base = base.lower()
    # 4. Replace non-alphanumeric with hyphens
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    # 5. Collapse duplicates
    base = re.sub(r'-{2,}', '-', base)
    # 6. Optionally truncate & hash for uniqueness
    if len(base) > max_length:
        h = hashlib.sha1(base.encode()).hexdigest()[:8]
        base = base[: max_length - len(h) - 1].rstrip('-') + '-' + h
    return base
class Video:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_id = video_path_mgr.get_video_id(self.video_path)
        self.info = video_path_mgr.get_info_data(video_path=self.video_path,
                                                 video_id=self.video_id)
        self.video_metadata = extract_video_metadata(video_id=self.video_id,
                                                     info_data=self.info)
        self.publication_date = self.info.get("publication_date",
                                              publication_date)
        self.basename = os.path.basename(self.video_path)
        self.filename,self.ext = os.path.splitext(self.video_path)
        self.title = self.filename
        self.video_url = generate_media_url(self.video_path)
        self.info['video_metadata']=self.video_metadata
        self.info['publication_date']=self.publication_date
        self.info['basename']=self.basename
        self.info['filename']=self.filename
        self.info['title']=self.title
        self.info['ext']=self.ext
        self.info['video_url']=self.video_url
        self.info['video_embed']=get_video_embed(self.video_id,
                                                 info_data=self.info)
        self.info = get_audio_file(video_id=self.video_id,
                                   info_data=self.info)
        self.info['thumbnails_dir'] = make_dirs(self.info['directory'],'thumbnails_directory')
        self.info = get_text_and_keywords(self.info, summarizer=summarizer, kw_model=kw_model)
        self.info['video_text']=analyze_video_text(self.video_path,output_dir=self.info['thumbnails_dir'],video_text=self.info['whisper_result']['text'])
        

    @property
    def thumbnail_url(self):
        return get_thumbnail_link(self.id, info_data=self.info)

    def schema_markup(self) -> Dict[str,Any]:
        return {
            "@context": "https://schema.org",
            "@type":    "VideoObject",
            "name":        self.title,
            "description": self.info.get("description", ""),
            "thumbnailUrl":self.thumbnail_url,
            "contentUrl":  get_video_link(self.id, info_data=self.info),
            "uploadDate":  self.info.get("publication_date", "")
        }

    def social_meta(self):
        return create_video_social_metadata(video_id=self.id,info_data=self.info)

    def as_frontend(self) -> Dict[str,Any]:
        return {
            "id":             self.video_id,
            "title":          self.title,
            "embed":          get_video_embed(self.video_id, info_data=self.info),
            "publication_date": self.info.get("publication_date",""),
            "description":    self.info.get("description",""),
            "keywords_str":   self.info.get("keywords_str",""),
            "thumbnail_url":  self.thumbnail_url,
            "contentUrl":     self.video_url,
            

        }
    def get_back_end(self):
            return {
                "file_metadata":  extract_video_metadata(self.id, info_data=self.info),
                "schema_markup":  self.schema_markup(),
                "social_meta":    self.social_meta()
                }



for basename in os.listdir(VIDEOS_DIR):
    
    data={"basename":basename}
    url='https://thedailydialectics.com/api/hard_coded_video_info'
    response = postRequest(url,data)


