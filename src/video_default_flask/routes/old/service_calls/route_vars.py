import os,sys,unicodedata,hashlib

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
import whisper
SAMPLE_RATE = whisper.audio.SAMPLE_RATE  # 16000 Hz
from abstract_utilities.type_utils import MEDIA_TYPES
from abstract_utilities.json_utils import *
from ..abstract_ocr.functions import *
from abstract_webserver import *

def get_media_types(*types):
    type_list = []
    for typ in types:
        if isinstance(typ,list):
            type_list+=typ
        if isinstance(typ,str):
            type_list.append(typ)
    ext_list = []
    for typ in type_list:
        varis = MEDIA_TYPES.get(typ)
        ext_list+=list(varis)
    return ext_list
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
    if not isinstance(info_data,dict):
        if info_data and isinstance(info_data,str) and os.path.exists(info_data):
            if os.path.isdir(info_data):
                info_temp = os.path.isdir(dirname,'info.json')
                dirname = os.path.dirname(info_data)
                basename = os.path.basename(dirname)
                return basename
            if os.path.isfile(info_data):
                info_temp = os.path.isdir(dirname,'info.json')
                dirname = os.path.dirname(info_data)
                basename = os.path.basename(dirname)
                return basename
      
                
        info_data =  kwargs
    info_dir = info_data.get('info_dir') or info_data.get('info_directory')
    video_id = info_data.get('video_id')
    video_path = info_data.get('video_path')
    if info_dir:
        video_id = os.path.basename(info_dir)
    if video_path:
        video_id = generate_file_id(video_path)
    if video_id:
        return video_id
    logger.info(f"NOM IT!!!!!{kwargs}")
