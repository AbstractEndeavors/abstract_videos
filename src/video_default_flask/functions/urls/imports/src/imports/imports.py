import os,re,unicodedata,hashlib,math,os,ffmpeg
from random import randrange
from PIL import Image
from datetime import datetime
from abstract_math import divide_it
from abstract_utilities import safe_read_from_json,is_number,get_logFile
from typing import *
from abstract_webserver import *
import os
from urllib.parse import quote  # to URL-encode spaces, etc.

BASE_URL = "https://typicallyoutliers.com"
PDFS_DIR = '/var/www/typicallyoutliers/frontend/public/pdfs/'
IMGS_DIR = '/var/www/typicallyoutliers/frontend/public/imgs/'
TEXT_DIR = '/var/www/typicallyoutliers/frontend/public/repository/text_dir/'
VIDEO_DIR = '/var/www/typicallyoutliers/frontend/public/repository/Video/'
REPO_DIR   = "/var/www/typicallyoutliers/frontend/public/repository/"
DIR_LINKS = {REPO_DIR:'repository',TEXT_DIR:'infos',VIDEO_DIR:'videos',PDFS_DIR:'pdfs',IMGS_DIR:'imgs'}
# map each extension to the URL prefix you want:
EXT_TO_PREFIX = {
    # images → /infos/
    **dict.fromkeys(
        {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'},
        'infos'
    ),
    # videos → /videos/
    **dict.fromkeys(
        {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'},
        'videos'
    ),
    # pdfs → /pdfs/
    '.pdf': 'pdfs',
    # audio → /audios/   (if you want)
    **dict.fromkeys({'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}, 'audios'),
    # documents → /docs/
    **dict.fromkeys({'.doc', '.docx', '.txt', '.rtf'}, 'docs'),
    # presentations → /slides/
    **dict.fromkeys({'.ppt', '.pptx'}, 'slides'),
    # spreadsheets → /sheets/
    **dict.fromkeys({'.xls', '.xlsx', '.csv'}, 'sheets')
}
publication_date = datetime.now().strftime("%Y-%m-%d")

def get_video_embed(video_id=None,info_data=None):
    video_url = get_video_link(video_id=video_id,info_data=info_data)
    video_embed = f'<video controls width="640" height="480"><source src="{video_url}" type="video/mp4">Your browser does not support the video tag.</video>'
    return video_embed
def generate_media_url(fs_path: str) -> str | None:
    """
    Given an absolute path under public/repository/,
    return the external URL for it (or None if it's outside).
    """
    # make sure we have a normalized absolute path
    fs_path = os.path.abspath(fs_path)
    
    # ensure it's actually under your repository folder
    if not fs_path.startswith(REPO_DIR):
        return None

    # compute the relative path inside repository/ and URL-encode it
    rel_path = fs_path[len(REPO_DIR):]
    rel_path = quote(rel_path.replace(os.sep, '/'))

    # pick a prefix based on extension, default to "repository"
    ext = os.path.splitext(fs_path)[1].lower()
    prefix = EXT_TO_PREFIX.get(ext, 'repository')

    # build the final URL
    return f"{BASE_URL}/{prefix}/{rel_path}"

def get_link(path):
    if path:
        for key,value in DIR_LINKS.items():
            if path.startswith(key):
                rel_path = path[len(key):]
                link = f"{BASE_URL}/{value}/{rel_path}"
                return link
logger = get_logFile('video_utils')
BASE_URL = "https://typicallyoutliers.com"
TEXT_DIR = '/var/www/typicallyoutliers/frontend/public/repository/text_dir/'
VIDEO_DIR = '/var/www/typicallyoutliers/frontend/public/repository/Video/'
DIR_LINKS = {TEXT_DIR:'infos',VIDEO_DIR:'videos'}

def get_file_parts(file_path):
    dirname = os.path.dirname(file_path)
    dirbase = os.path.basename(dirname)
    
    basename = os.path.basename(file_path)
    filename,ext = os.path.splitext(basename)
    return {"file_path":file_path,
            "dirbase":dirbase,
            "dirname":dirname,
            "basename":basename,
            "filename":filename,
            "ext":ext}
def generate_video_id(path: str, max_length: int = 50) -> str:
    # 1. Take basename (no extension)
    file_parts = get_file_parts(path)
    base= file_parts.get("filename")
    if base == 'video':
        base = file_parts.get("dirbase")
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

def get_file_size(file_path):
    if file_path and os.path.isfile(file_path):
        raw_file_size = os.path.getsize(file_path)
        if is_number(raw_file_size):
            return divide_it(raw_file_size,1024)  # KB
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
def extract_video_metadata(video_id=None,info_data=None):
    video_path = get_video_path(video_id=video_id,info_data=info_data)
    probe = ffmpeg.probe(video_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    if not video_stream:
        print(f"Warning: No video stream found in {video_path}")
        return {}
    metadata = {
        "resolution": "1280x720",
        'duration': float(probe['format']['duration']),
        'width': int(video_stream['width']),
        'height': int(video_stream['height']),
        'file_size': get_file_size(video_path),
        'format': probe['format']['format_name'],
        'video_codec': video_stream.get('codec_name', ''),
        'audio_codec': audio_stream.get('codec_name', '') if audio_stream else '',
        'mime_type': 'video/mp4' if video_path.endswith('.mp4') else 'video/webm' if video_path.endswith('.webm') else 'video/unknown'
    }
    return metadata
   
def get_item_from_info(info: Dict[str, Any], key: str) -> Optional[str]:
    """
    Extract URL for `key` from info dict, supporting nested file_path keys.
    """
    item = info.get(key)
    if isinstance(item, dict):
        path = item.get("file_path") or item.get("path")
    else:
        path = item
    return get_link(path) if isinstance(path, str) else None


def get_all_available_videos(text_dir: str = TEXT_DIR) -> List[str]:
    """
    List all subdirectories in text_dir containing info.json.
    """
    return [p.name for p in Path(text_dir).iterdir() if p.is_dir() and (p / "info.json").is_file()]

def get_info_path(video_id):
    info_path = os.path.join(TEXT_DIR, video_id, 'info.json')
    return info_path

def get_thumbnails_directory(video_id=None,info_data=None,thumbnail_path=None):
    if thumbnail_path and os.path.isfile(thumbnail_path):
        return os.path.dirname(thumbnail_path)
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    thumbnails_directory = info_data.get('thumbnails_directory')
    return thumbnails_directory
def get_thumbnail_data(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    thumbnail_data = info_data.get('thumbnail')
    return thumbnail_data
def get_rndm_thumbnail(video_id=None,info_data=None,thumbnail_path=None,thumbnails_directory=None,min_frame=None,max_frame=None):
    thumbnails_directory = thumbnails_directory or get_thumbnails_directory(video_id=video_id,info_data=info_data,thumbnail_path=thumbnail_path)
    thumbnail_items = os.listdir(thumbnails_directory)
    thumbnail_item_length = len(thumbnail_items)
    min_frame= min_frame or 0
    max_frame = thumbnail_item_length - 1
    if thumbnail_item_length:
        if thumbnail_item_length >80:
            min_frame = 35
        else:
            min_frame=min_frame or 0
        if thumbnail_item_length >65:
            max_frame = thumbnail_item_length-80
        else:
            max_frame = max_frame or thumbnail_item_length
        
        if min_frame>=max_frame:
            thumbnail_num = min_frame+1
        else:
            thumbnail_num = randrange(min_frame,max_frame)
        if not  thumbnails_directory or not thumbnail_items:
            return '/var/www/typicallyoutliers/frontend/public/imgs/no_image.jpg'
        thumbnail_path = os.path.join(thumbnails_directory,thumbnail_items[thumbnail_num])
        return thumbnail_path
    return '/var/www/typicallyoutliers/frontend/public/imgs/no_image.jpg'
def get_thumbnail_items(video_id=None,info_data=None,thumbnail_path=None,thumbnails_directory=None):
    thumbnails_directory = thumbnails_directory or get_thumbnails_directory(video_id=video_id,info_data=info_data,thumbnail_path=thumbnail_path)
    return os.listdir(thumbnails_directory)
    
def get_thumbnail_frame(video_id=None,info_data=None,thumbnail_path=None):
    thumbnail_path = thumbnail_path or get_thumbnail_path(video_id=video_id,info_data=info_data)
    basename = thumbnail_path
    if thumbnail_path and os.path.isfile(thumbnail_path):
        basename = os.path.basename(thumbnail_path)
    filename,ext = os.path.splitext(basename)
    frame_number = filename.split('_')[-1]
    if is_number(frame_number):
        return int(frame_number)
def is_within_frames(video_id=None,info_data=None,thumbnail_path=None):
    thumbnails_directory = thumbnail_path
    if thumbnail_path and os.path.isfile(thumbnail_path):
        thumbnails_directory = os.path.dirname(thumbnail_path)
    thumbnail_frame = get_thumbnail_frame(video_id=video_id,info_data=info_data,thumbnail_path=thumbnail_path)
    
    thumbnails = get_thumbnail_items(video_id=video_id,info_data=info_data,thumbnail_path=thumbnail_path,thumbnails_directory=thumbnails_directory)
    if thumbnail_frame < 70:
        return False
    thumbnails_length = len(thumbnails)
    max_frame = thumbnails_length-80
    if max_frame>0 and max_frame<thumbnail_frame:
        return False
    return True
def assure_valid_thumbnail(video_id=None,info_data=None,thumbnail_path=None,thumbnails_directory=None):
    thumbnail_path = thumbnail_path or get_thumbnail_path(video_id=video_id,info_data=info_data)
    if thumbnail_path:  
        if not is_within_frames(video_id=video_id,info_data=info_data,thumbnail_path=thumbnail_path):
            thumbnail_path = get_rndm_thumbnail(video_id=video_id,info_data=info_data,thumbnail_path=thumbnail_path,thumbnails_directory=thumbnails_directory)
    return thumbnail_path
def get_thumbnail_path(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    thumbnail_data = get_thumbnail_data(video_id=video_id,info_data=info_data)
    thumbnails_directory = get_thumbnails_directory(video_id=video_id,info_data=info_data)
    if not thumbnail_data:
        
        file_path = get_rndm_thumbnail(video_id=video_id,info_data=info_data)
    else:
        file_path = thumbnail_data.get('file_path')
    if len(os.listdir(thumbnails_directory))>80:
    
        file_path = assure_valid_thumbnail(video_id=video_id,info_data=info_data,thumbnail_path=file_path,thumbnails_directory=thumbnails_directory)
    return file_path
def get_thumbnail_alt(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    thumbnail_data = get_thumbnail_data(video_id=video_id,info_data=info_data)
    if not thumbnail_data:
        alt_text = get_video_description(video_id=video_id,info_data=info_dat)
    else:
        alt_text = thumbnail_data.get('alt_text')
    return alt_text
def get_thumbnail_metadata(video_id=None,info_data=None):
    thumbnail_path = get_thumbnail_path(video_id=video_id,info_data=info_data)
    image_metadata = get_image_metadata(thumbnail_path)
    return image_metadata
def get_thumbnail_seo_data(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    thumbnail_data = get_thumbnail_data(video_id=video_id,info_data=info_data)
    if not thumbnail_data:
        alt_text = get_video_description(video_id=video_id,info_data=info_dat)
    else:
        alt_text = thumbnail_data.get('alt_text')
    return alt_text
def get_video_id(video_id=None,info_data=None):
    if not video_id: 
        info_data = get_video_info_data(video_id=video_id,info_data=info_data)
        video_id = info_data.get('video_id') or info_data.get('filename') or "Untitled Video"
    return video_id
def get_thumbnail_link(video_id=None,info_data=None):
    thumbnail_path = get_thumbnail_path(video_id=video_id,info_data=info_data)
    basename = os.path.basename(thumbnail_path)
    filename,ext = os.path.splitext(basename)
 
    thumbnail_link = get_link(thumbnail_path)
    return thumbnail_link
def get_audio_path(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    audio_path = info_data.get('audio_path')
    return audio_path
def get_audio_link(video_id=None,info_data=None):
    audio_path = get_audio_path(video_id=video_id,info_data=info_data)
    audio_link = get_link(audio_path)
    return audio_path
def get_video_path(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    video_path = info_data.get('video_path')
    return video_path
def get_video_link(video_id=None,info_data=None):
    video_path = get_video_path(video_id=video_id,info_data=info_data)
    video_link = get_link(video_path)
    return video_link
def get_keywords(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    keywords = info_data.get('combined_keywords', []) or info_data.get('keywords', []) or [video_id]
    return keywords
def get_keywords_str(video_id=None,info_data=None):
    keywords = get_keywords(video_id=video_id,info_data=info_data)
    return ", ".join(keywords)
def get_video_description(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    description = info_data.get("seo_description","Check out this video")
    return description
def get_video_title(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    title = info_data.get("seo_title") or get_video_id(video_id=video_id,info_data=info_data)
    return title
def get_whisper_result(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    whisper_result = info_data.get("whisper_result") or get_video_id(video_id=video_id,info_data=info_data)
    return whisper_result
def get_whisper_text(video_id=None,info_data=None):
    whisper_result = get_whisper_result(video_id=video_id,info_data=info_data)
    if isinstance(whisper_result,dict):
        text = whisper_result.get("text")
    else:
        text = whisper_result
    return text
def get_whisper_segments(video_id=None,info_data=None):
    whisper_result = get_whisper_result(video_id=video_id,info_data=info_data)
    if isinstance(whisper_result,dict):
        segments = whisper_result.get("segments")
    else:
        segments = whisper_result
    return segments
def get_video_embed(video_id=None,info_data=None):
    video_url = get_video_link(video_id=video_id,info_data=info_data)
    video_embed = f'<video controls width="640" height="480"><source src="{video_url}" type="video/mp4">Your browser does not support the video tag.</video>'
    return video_embed
def get_publication_date(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    publication_date = info_data.get("publication_date") or datetime.now().strftime("%Y-%m-%d")
    return publication_date
def get_video_social_metadata(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    social_metadata = info_data.get("social_metadata") or create_video_social_metadata(video_id=video_id,info_data=info_data)
    for key,value in social_metadata.items():
        if isinstance(value,str):
            if value.startswith('/var/www'):
                social_metadata[key] = get_link(value)
    return social_metadata
def get_video_schema_markup(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    schema_markup = info_data.get("schema_markup") or create_video_schema_markeup(video_id=video_id,info_data=info_data)
    for key,value in schema_markup.items():
        if isinstance(value,str):
            if value.startswith('/var/www'):
                schema_markup[key] = get_link(value)
    return schema_markup
def get_video_captions_path(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    captions_path = info_data.get("captions_path")
    return captions_path
def get_video_captions_link(video_id=None,info_data=None):
    video_captions_path = get_video_captions_path(video_id=video_id,info_data=info_data)
    video_captions_link = get_link(video_captions_path)
    return video_captions_link
def get_video_captions_data(video_id=None,info_data=None):
    video_captions_path = get_video_captions_path(video_id=video_id,info_data=info_data)
    video_captions = read_from_file(video_captions_path)
    return video_captions

def get_video_duration(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    video_duration = info_data.get("duration_seconds")
    return video_duration
def get_video_file_metadata(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    video_metadata = info_data.get("file_metadata") or create_video_meta_data(video_id=video_id,info_data=info_data)
    return video_metadata

def get_video_info_data(video_id=None,info_data=None):
    info_path=None
    if video_id==None and info_data==None:
        return
    if info_data:
        return info_data
    if video_id:
        info_path = get_info_path(video_id)
    if info_path:
        if os.path.isfile(info_path):
            info_data = safe_read_from_json(info_path)
            return info_data
    return {}

def get_thumbnail_info(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    thumbnail_path = get_thumbnail_path(video_id=video_id,info_data=info_data)
    thumbnail_basename = os.path.basename(thumbnail_path)
    thumbnail_filename,thumbnail_ext = os.path.filename(thumbnail_basename)
    thumbnail_metadata = get_thumbnail_metadata(video_id=video_id,info_data=info_data)
    thumbnail_file_size = thumbnail_metadata.get("file_size")
    thumbnail_dimensions = thumbnail_metadata.get('dimensions')
    thumbnail_height = thumbnail_dimensions.get('height')
    thumbnail_width = thumbnail_dimensions.get('width')
    thumbnail_dimensions_str = f"({thumbnail_width}×{thumbnail_height})"
    thumbnail_title = f"{thumbnail_filename} {thumbnail_dimensions_str}"
    alt_text = get_thumbnail_alt(video_id=video_id,info_data=info_data)
    thumbnail_url = get_thumbnail_link(video_id=video_id,info_data=info_data)
    video_url = get_video_link(video_id=video_id,info_data=info_data)
    description = get_video_description(video_id=video_id,info_data=info_data)
    publication_date = get_publication_date(video_id=video_id,info_data=info_data)
    info = {
        "alt": alt_text,
        "caption": description,
        "keywords_str": keywords_str,
        "filename": thumbnail_filename,
        "ext": thumbnail_ext,
        "title": thumbnail_title,
        "dimensions": thumbnail_dimensions,
        "file_size": thumbnail_file_size,
        "license": "CC BY-SA 4.0",
        "attribution": "Created by thedailydialectics for educational purposes",
        "longdesc": description,
        "schema": {
            "@context": "https://schema.org",
            "@type": "ImageObject",
            "name": thumbnail_filename,
            "description": description,
            "url": thumbnail_url,
            "contentUrl": video_url,
            "width": thumbnail_width,
            "height": thumbnail_height,
            "license": "https://creativecommons.org/licenses/by-sa/4.0/",
            "creator": {"@type": "Organization", "name": "thedailydialectics"},
            "datePublished": publication_date
        },
        "social_meta": {
            "og:image": thumbnail_url,
            "og:image:alt": alt_text,
            "twitter:card": "summary_large_image",
            "twitter:image": thumbnail_url
        }
    }
    return info

def create_video_schema_markeup(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    video_url= get_video_link(video_id=video_id,info_data=info_data)
    thumbnail_url = get_thumbnail_link(video_id=video_id,info_data=info_data)
    description = get_video_description(video_id=video_id,info_data=info_data)
    title = get_video_title(video_id=video_id,info_data=info_data)
    keywords = get_keywords(video_id=video_id,info_data=info_data)
    publication_date = get_publication_date(video_id=video_id,info_data=info_data)
    video_duration = get_video_duration(video_id=video_id,info_data=info_data)
    return {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": title,
        "description": description,
        "thumbnailUrl":thumbnail_url,
        "duration": video_duration,
        "uploadDate": publication_date,
        "contentUrl": video_url,
        "keywords": keywords,
        "accessibilityFeature": ["captions"]
    }
def create_video_social_metadata(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    video_url= get_video_link(video_id=video_id,info_data=info_data)
    thumbnail_url = get_thumbnail_link(video_id=video_id,info_data=info_data)
    description = get_video_description(video_id=video_id,info_data=info_data)
    title = get_video_title(video_id=video_id,info_data=info_data)
    video_duration = get_video_duration(video_id=video_id,info_data=info_data)
    return {
        "og:title": title,
        "og:description": description,
        "og:image": thumbnail_url,
        "og:video": video_url,
        "twitter:card": "player",
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image": thumbnail_url
    }
def create_video_meta_data(video_id=None,info_data=None):
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    video_path = get_thumbnail_path(video_id=video_id,info_data=info_data)
    video_basename = os.path.basename(video_path)
    video_filename,video_ext = os.path.filename(video_basename)
    video_format = str(video_ext[1:]).upper() 
    return {
            "resolution": "1280x720",
            "format": video_format,
            "file_size_mb": get_file_size(video_path)
        }

def get_video_data(video_id=None,info_data=None):
    """Format video data to match frontend get_video_data function."""
    info_data = get_video_info_data(video_id=video_id,info_data=info_data)
    video_url= get_video_link(video_id=video_id,info_data=info_data)
    if video_url:
        basename = os.path.basename(video_url)
        filename,ext = os.path.splitext(basename)
        
        thumbnail_url = get_thumbnail_link(video_id=video_id,info_data=info_data)
        description = get_video_description(video_id=video_id,info_data=info_data)
        title = get_video_title(video_id=video_id,info_data=info_data)
        keywords_str = get_keywords_str(video_id=video_id,info_data=info_data)
        video_captions = get_video_captions_link(video_id=video_id,info_data=info_data)
        whisper_text = get_whisper_text(video_id=video_id,info_data=info_data)
        whisper_segments = get_whisper_segments(video_id=video_id,info_data=info_data)
        video_embed = get_video_embed(video_id=video_id,info_data=info_data)
        publication_date = get_publication_date(video_id=video_id,info_data=info_data)
        return {
            "id": video_id,
            "title": title,
            "embed": video_embed,
            "description": description,
            "keywords_str": keywords_str,
            "thumbnail_url": thumbnail_url,
            "contentUrl": video_url,
            "video_url":video_url,
            "optimized_video_url": video_url,
            "ext": ext,
            "mime_type": "video/mp4",
            "category": "Education",
            "transcript": whisper_text,
            "captions": video_captions,
            "schema_markup": get_video_schema_markup(video_id=video_id,info_data=info_data),
            "social_meta": get_video_social_metadata(video_id=video_id,info_data=info_data),
            "category": "General",
            "publication_date": publication_date,
            "file_metadata": extract_video_metadata(video_id=video_id,info_data=info_data)
        }
def get_intial_video_data(video_path):
    dirname = os.path.dirname(video_path)
    basename = os.path.basename(video_path)
    filename,ext = os.path.splitext(basename)
    video_id = generate_video_id(path=video_path, max_length=50)
    video_dir = make_dirs(dirname,video_id)
    shutil.move(video_path,video_dir)
    get_link(thumbnail_path)
    video_url= get_video_link(video_id=video_id,info_data=info_data)
    video_embed = get_video_embed(video_id=video_id,info_data=info_data)
    basename = os.path.basename(video_url)
    filename,ext = os.path.splitext(basename)
    {
        "id": video_id,
        "title": title,
        "embed": video_embed,
        "contentUrl": video_url,
        "video_url":video_url,
        "optimized_video_url": video_url,
        "ext": ext,
        "mime_type": "video/mp4",
        "category": "Education",
        "publication_date": publication_date,
        "file_metadata": extract_video_metadata(video_id=video_id,info_data=info_data)
}
