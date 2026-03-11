import os,sys

from multiprocessing import Process
from flask import (
    Blueprint,
    request,
    jsonify,
    send_file
)
from flask_cors import CORS
from abstract_flask import get_request_data
from werkzeug.utils import secure_filename
from abstract_utilities import (
    safe_read_from_json,
    get_logFile,
    safe_dump_to_file
)
from typing import *
from abstract_utilities.type_utils import get_media_types
#from ..functions import *
from abstract_webserver import *
ALLOWED_EXTENSIONS = get_media_types(['video','image'])  # Add more as needed
logOn=True
DOMAIN='https://typicallyoutliers.com'
UPLOADER='The Daily Dialectics'
MAIN_DIR = "/var/www/typicallyoutliers"
FRONTEND_DIR = f"{MAIN_DIR}/frontend"

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
def isLogOn(logger_func,filepath,endpoint,data=None):
    string = f"""filepath: {filepath}
endpoint: {endpoint}
data: {data}
"""
    if logOn:
        logger_func(string)
    return string
def log_error(logger_func,log_string,error_string):
    string = f"{log_string}\n ERROR: {error_string}"
    logger_func.error(string)
    return jsonify({"error":error_string})
def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def get_info_from_video_id(video_id=None, info=None):
    """Retrieve video info from the JSON file corresponding to video_id."""
    if video_id is not None and info is None:
        file_path = f"{VIDEOS_URL}/{video_id}/info.json"
        if os.path.exists(file_path):
            info = safe_read_from_json(file_path)
    return info
def initiate_process(target,*args):
    p = Process(target=target, args=args)
    p.start()
    logger.info(f"Started process for: {args}")

directory_links={"videos":{"directory":VIDEOS_DIR,"link":VIDEOS_URL},'imgs':{"directory":IMGS_DIR,"link":IMGS_URL}}
server_mgr = serverManager(src_dir=SRC_DIR,public_dir=PUBLIC_DIR,main_dir=FRONTEND_DIR,domain=DOMAIN,directory_links=directory_links)
STATIC_DIR = server_mgr.static_dir or STATIC_DIR
directory_links = server_mgr.directory_links
STATIC_URL_PATH  = directory_links.get('static',{}).get('link') or '/media/static'
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

def get_bp(name,static_folder=None,static_url_path=None):
    if name and isinstance(name,str) and os.path.isfile(name):
        basename = os.path.basename(name)
        name,ext = os.path.splitext(basename)
    bp_name = f"{name}_bp"
    logger = get_logFile(bp_name)
    logger.info(f"Python path: {sys.path}")
    bp_var = Blueprint(
        bp_name, 
        __name__, 
        static_folder=STATIC_DIR,
        static_url_path= STATIC_URL_PATH
    )
    return bp_var,logger
def get_arg_name(json_obj,i=None):
    arg_name = 'arg'
    i = i or 0
    while True:
        if kwargs.get(arg_name):
            arg_name = f'arg_{i}'
        else:
            return arg_name
        i+=1
def safe_key_extract(key,json_obj=None):
    json_obj = json_obj or {}
    value = None
    if json_obj and isinstance(json_obj,dict):
        if key:
            value = json_obj.get(key)
    return value
def update_json_data(json_data,update_data,keys=None):
    valid_keys=None
    invalid_keys=None
    if keys == True:
        valid_keys=VALID_KEYS
        invalid_keys=INVALID_KEYS
        values_string = ''
        for key,value in update_data.items():
            values_string+= f"{key} == {value}\n"
        
        logger.info(f"new_datas:\n{values_string}")
        keys = invalid_keys
    
    json_data = safe_update_json_datas(json_data=json_data,
                            update_data=update_data,
                            valid_keys=valid_keys,
                            invalid_keys=invalid_keys
                            ) 
    
    return json_data
def get_info_data_from_data(data):
    info_data = data.get('json_data',{}) or data.get('info_data',{}) or data.get('data',{}) or data.get('info',{})
    return info_data
def get_request_info_data(req):
    data = get_request_data(req)
    info_data = get_info_data_from_data(data)
    data = update_json_data(data,info_data)
    info_data = update_json_data(info_data,data,keys=True)
    return data,info_data
def get_from_data_or_info(key,*args,**kwargs):
    key_value = None
    for i,arg in enumerate(args):
        arg_name = get_arg_name(kwargs,i=i)
        kwargs[arg_name] = arg
    for key,value in kwargs.items():
        key_value = safe_key_extract(key,value)
        if key_value:
            break
    return key_value
