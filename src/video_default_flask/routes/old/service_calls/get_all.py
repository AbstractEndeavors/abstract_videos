from abstract_ocr import extract_audio_from_video,analyze_video_text,get_video_info_data
from abstract_utilities import get_all_file_types
import unicodedata,re,os,hashlib
from functions import *
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

def get_local_path(path):
    prefix = '/run/user/1000/gvfs/sftp:host=192.168.0.100,user=solcatcher'
    if not os.path.exists(path):
        path = f"{prefix}{path}"
    if os.path.exists(path):
        return path
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
    ip = new_data['info_directory']
    vp = new_data['video_path']
    ap = new_data['audio_path']
    vi = new_data['video_id']
    td = new_data.get('thumbnails_directory')
    
    thumbnails_dir = os.path.join(ip,'thumbnails')
    # 2) Ensure audio exists
    if vp and ap and not os.path.isfile(ap):
        try:
            result = extract_audio_from_video(video_path=vp, audio_path=ap)
            if result:
                info_data['audio_path'] = ap
        except Exception as e:
            logger.info(f"{e}")
    # 3) Ensure at least one thumbnail exists
    
    if td == None or vp and td and not any(os.scandir(td)) or not os.path.isdir(thumbnails_dir):
        try:
            thumbnails_dir = os.path.join(ip,'thumbnails')
            new_data['thumbnails_directory'] = thumbnails_dir
            os.makedirs(thumbnails_dir,exist_ok=True)
            thumbs = analyze_video_text(video_path=vp,
                           directory=thumbnails_dir,
                           remove_phrases=REMOVE_PHRASES,
                           video_id=vi)
            # e.g. create_thumbnails returns a list of file‐paths
            info_data['thumbnails'] = thumbs
        except Exception as e:
            logger.info(f"{e}")
    # 4) Persist your updates back into info.json
    safe_save_updated_json_data(
        data={'audio_path': info_data.get('audio_path'),
              'thumbnails': info_data.get('thumbnails', [])},
        file_path=get_video_info_path(**info_data),
        valid_keys=['audio_path', 'thumbnails'],
        invalid_keys=[]
    )

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
TEXT_DIR = "/var/www/typicallyoutliers/frontend/public/repository/text_dir"
VIDEOS_DIR = "/var/www/typicallyoutliers/frontend/public/repository/videos"
available_list = get_all_file_types('video',get_local_path(VIDEOS_DIR))
for video_path in available_list:
    video_id = generate_file_id(video_path)
    input(video_id)
    updated = get_initial_info_data(video_path=video_path,video_id=video_id)
    input(updated)
