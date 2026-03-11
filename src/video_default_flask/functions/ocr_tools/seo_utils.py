from .text_utils import *
from .audio_utils import *
from urllib.parse import quote
from .functions import (logger,
                        create_key_value,
                        os,
                        timestamp_to_milliseconds,
                        format_timestamp,
                        get_time_now_iso,
                        parse_timestamp,
                        url_join,
                        get_whisper_result_data)
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from datetime import datetime
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
def generate_with_bigbird(text: str, task: str = "title", model_dir: str = "allenai/led-base-16384") -> str:
    try:
        tokenizer = LEDTokenizer.from_pretrained(model_dir)
        model = LEDForConditionalGeneration.from_pretrained(model_dir)
        prompt = (
            f"Generate a concise, SEO-optimized {task} for the following content: {text[:1000]}"
            if task in ["title", "caption", "description"]
            else f"Summarize the following content into a 100-150 word SEO-optimized abstract: {text[:4000]}"
        )
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(
            inputs["input_ids"],
            max_length=200 if task in ["title", "caption"] else 300,
            num_beams=5,
            early_stopping=True
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Error in BigBird processing: {e}")
        return ""
def generate_media_url(fs_path: str,domain=None,repository_dir=None) -> str | None:
    fs_path = os.path.abspath(fs_path)
    if not fs_path.startswith(REPO_DIR):
        return None
    rel_path = fs_path[len(REPO_DIR):]
    rel_path = quote(rel_path.replace(os.sep, '/'))
    ext = os.path.splitext(fs_path)[1].lower()
    prefix = EXT_TO_PREFIX.get(ext, 'repository')
    return f"{domain}/{prefix}/{rel_path}"
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
def generate_info_json(filepath=None,
                        prompt=None,
                        alt_text=None,
                        title=None,
                        description=None,
                        keywords=None,
                        domain=None,
                        video_path=None,
                        repository_dir=None,
                        generator=None,
                        LEDTokenizer=None,
                        LEDForConditionalGeneration=None):
    """
    Build structured info.json for an image, including SEO schema and social metadata.
    """
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    filename,ext = os.path.splitext(basename)
    url_path = filepath
    title_prompt = generate_with_bigbird(f"Video of {filename.replace('-', ' ')} with the video text f{alt_text}", task="title")
    description_prompt = generate_with_bigbird(f"Video of {filename.replace('-', ' ')} with the video text f{alt_text}", task="description")
    caption_prompt = generate_with_bigbird(f"Video of {filename.replace('-', ' ')} with the video text f{alt_text}", task="caption")
    img_meta = get_image_metadata(str(filepath)) if os.path.isfile(filepath) else {"dimensions": {"width": 0, "height": 0}, "file_size": 0.0}
    dimensions = img_meta.get("dimensions",{})
    width = dimensions.get('width')
    height = dimensions.get('height')
    file_size = img_meta.get("file_size")
    description = alt_text
    title = filename
    caption = alt_text
    if generator:
        gen = generator(prompt, max_length=100, num_return_sequences=1)[0]
        description = gen.get('generated_text', '')[:150]
    description = alt_text
    title = title or filename
    caption = caption or alt_text
    info = {
        "alt": alt_text,
        "caption": alt_text,
        "keywords_str": keywords,
        "filename": filename,
        "ext": f"{ext}",
        "title": f"{title} ({width}×{height})",
        "dimensions": dimensions,
        "file_size": file_size,
        "license": "CC BY-SA 4.0",
        "attribution": "Created by thedailydialectics for educational purposes",
        "longdesc": description,
        "schema": {
            "@context": "https://schema.org",
            "@type": "ImageObject",
            "name": filename,
            "description": description,
            "url": generate_media_url(filepath,domain=domain,repository_dir=repository_dir),
            "contentUrl": generate_media_url(video_path,domain=domain,repository_dir=repository_dir),
            "width": width,
            "height": height,
            "license": "https://creativecommons.org/licenses/by-sa/4.0/",
            "creator": {"@type": "Organization", "name": "thedailydialectics"},
            "datePublished": datetime.now().strftime("%Y-%m-%d")
        },
        "social_meta": {
            "og:image": generate_media_url(filepath,domain=domain,repository_dir=repository_dir),
            "og:image:alt": alt_text,
            "twitter:card": "summary_large_image",
            "twitter:image": generate_media_url(filepath,domain=domain,repository_dir=repository_dir)
        }
    }
    return info

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
import math
from .functions import logger

def _format_srt_timestamp(seconds: float) -> str:
    """
    Convert seconds (e.g. 3.2) into SRT timestamp "HH:MM:SS,mmm"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - math.floor(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def export_srt_whisper(whisper_json: dict, output_path: str):
    """
    Write an .srt file from Whisper's verbose_json format.
    `whisper_json["segments"]` should be a list of {start,end,text,...}.
    """
    logger.info(f"export_srt_whisper: {output_path}")
    segments = whisper_json.get("segments", [])
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, start=1):
            start_ts = _format_srt_timestamp(seg["start"])
            end_ts   = _format_srt_timestamp(seg["end"])
            text     = seg["text"].strip()
            f.write(f"{idx}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{text}\n\n")
def export_srt(audio_text, output_path):
    logger.info(f"export_srt: {output_path}")
    with open(output_path, 'w') as f:
        for i, entry in enumerate(audio_text, 1):
            start = entry['start_time'].replace('.', ',')
            end = entry['end_time'].replace('.', ',')
            f.write(f"{i}\n{start} --> {end}\n{entry['text']}\n\n")

def pick_optimal_thumbnail(video_text,
                           combined_keywords):
    scores = []
    for entry in video_text:
        
        text = entry['text'].lower()
        
        keyword_score = sum(1 for kw in combined_keywords or [] if kw.lower() in text)
        
        clarity_score = 1 if len(text.strip()) > 20 else 0  # basic clarity check
        
        end_phrase_penalty = -1 if "thanks for watching" in text else 0
        
        total_score = keyword_score + clarity_score + end_phrase_penalty
        
        scores.append((entry['frame'],
                       total_score,
                       text.strip()))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return scores[0] if scores else None
def get_frame_number(file_path):
    file_path = '.'.join(file_path.split('.')[:-1])
    return int(file_path.split('_')[-1])
    

def pick_optimal_thumbnail(whisper_result, keywords, thumbnails_directory,*args,**kwargs):
    scores = []
    dirbase = os.path.basename(os.path.dirname(thumbnails_directory))
    
    thumb_name,thumb_ext = os.path.splitext(os.listdir(thumbnails_directory)[0])
    thubnail_items = os.listdir(thumbnails_directory)
    thubnail_items_length = len(thubnail_items)
    if thubnail_items_length> 35:
        thubnail_items = thubnail_items[35:]
    thubnail_items_length = len(thubnail_items)
    if thubnail_items_length> 35:
        thubnail_items = thubnail_items[:-35]
    
    # Get list of thumbnails from directory
    thumbnails = sorted(
        [f for f in thubnail_items if f.endswith(".jpg")],
        key=lambda x: get_frame_number(x) 
    )
    
    # Process each Whisper segment
    for segment in whisper_result["segments"]:
        text = segment["text"].lower().strip()
        start_time = segment["start"]        # Find the closest thumbnail based on start time
        frame_number = math.floor(start_time)
        thumbnail_name = f"{dirbase}_frame_{frame_number}{thumb_ext}"
        
        # Check if thumbnail exists
        if thumbnail_name not in thumbnails:
            continue
        
        # Score the caption
        keyword_score = sum(1 for kw in keywords if kw.lower() in text)
        clarity_score = 1 if len(text) > 20 else 0
        end_phrase_penalty = -1 if "thanks for watching" in text else 0
        total_score = keyword_score + clarity_score + end_phrase_penalty
        
        # Store thumbnail path, score, and caption
        thumbnail_path = os.path.join(thumbnails_directory, thumbnail_name)
        scores.append((thumbnail_path, total_score, text))
        print(keywords)
    # Sort by score (highest first)
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    
    return scores[0] if scores else None



def get_from_list(list_obj=None,length=1):
    list_obj = list_obj or []
    if len(list_obj) >= length:
        list_obj = list_obj[:length]
    return list_obj
def get_seo_data(info_data,
                 uploader=None,
                 domain=None,
                 categories=None,
                 videos_url=None,
                 repository_dir=None,
                 directory_links=None,
                 videos_dir=None,
                 base_url=None,
                 generator=None,
                 LEDTokenizer=None,
                 LEDForConditionalGeneration=None,
                 **kwargs):
    info = info_data
    info = create_key_value(info,
                            'categories',
                            categories or {'ai': 'Technology', 'cannabis': 'Health', 'elon musk': 'Business'})
    
    info = create_key_value(info,
                            'uploader',
                            uploader or 'The Daily Dialectics')
    
    info = create_key_value(info,
                            'domain',
                            domain or 'https://thedailydialectics.com')
    
    info = create_key_value(info,
                            'videos_url',
                            videos_url or f"{info['domain']}/videos")
    video_path = info.get('video_path')
    if video_path == None:
        logger.info(f"video_path == {video_path}")
    for keyword_key in ['combined_keywords','keywords']:
        keywords = info.get(keyword_key,[])
        if keywords and len(keywords)>0:
            break
    filename = info.get('filename')
    if not filename:
        basename = os.path.basename(video_path)
        filename,ext = os.path.splitext(basename)
        info['basename'] = basename
        info['filename'] = filename
    info['title'] = info.get('title',filename)
    primary_keyword = keywords[0] if keywords and len(keywords)>0 else filename
    seo_title = f"{primary_keyword} - {info['title']}"
    seo_title = get_from_list(seo_title,length=70)
    info['seo_title'] = seo_title
    
    summary = info.get('summary','')
    summary_desc = get_from_list(summary,length=150)
    keywords = [f"{keyword}" for keyword in keywords if keyword]
    keywords_str = ', '.join(get_from_list(keywords,length=3))
    seo_desc = f"{summary_desc} Explore {keywords_str}. Visit thedailydialectics.com for more!"
    seo_description = get_from_list(seo_desc,length=300)
    info['seo_description'] = seo_description
    
    seo_tags = [kw for kw in keywords or [] if kw and isinstance(kw,str) and kw.lower() not in ['video','audio','file']]
    info['seo_tags'] = seo_tags
    
    video_text = info.get('video_text')
    info['thumbnail']={}
    if video_text and len(video_text)>0:
        thumnail_data = video_text[0]
        thumbnail_filepath = os.path.join(info['thumbnails_directory'],thumnail_data.get("frame"))
        info['thumbnail']['file_path'] = thumbnail_filepath
        
        thumbnail_alt_text = thumnail_data.get("text")
        info['thumbnail']['alt_text']= thumbnail_alt_text
        
    whisper_json = get_whisper_result_data(**info)
    thumbnail_score = pick_optimal_thumbnail(whisper_json,keywords,info["thumbnails_directory"])
    if thumbnail_score:
        best_frame, score, matched_text = thumbnail_score
        file_path = os.path.join(info['thumbnails_directory'],best_frame)
        info['thumbnail']['file_path']= file_path
        
        alt_text = get_from_list(matched_text,length=100)
        info['thumbnail']['alt_text']= alt_text
        
        basename = os.path.basename(file_path)
        filename,ext = os.path.splitext(basename)
        
        prompt = f"Generate SEO metadata for {filename} with the video text f{alt_text}"
        thumbnail_seo_data = generate_info_json(file_path,
                                                prompt,
                                                alt_text,
                                                seo_title,
                                                seo_description,
                                                keywords,
                                                domain,
                                                video_path,
                                                repository_dir,
                                                generator,
                                                LEDTokenizer,
                                                LEDForConditionalGeneration)
        info['thumbnail']['seo_data']= thumbnail_seo_data
    
    audio = AudioSegment.from_wav(info['audio_path'])

    duration_seconds = len(audio) / 1000
    info['duration_seconds'] = duration_seconds

    duration_formatted = format_timestamp(len(audio))
    info['duration_formatted'] = duration_formatted
    
    

    export_srt_whisper(
        whisper_json,
        os.path.join(info["info_directory"], "captions.srt")
    )
    
    info['captions_path'] = os.path.join(info['info_directory'],
                                         "captions.srt")
    
    info['schema_markup'] = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": info['seo_title'],
        "description": info['seo_description'],
        "thumbnailUrl": info['thumbnail']['file_path'],
        "duration": f"PT{int(info['duration_seconds'] // 60)}M{int(info['duration_seconds'] % 60)}S",
        "uploadDate": get_time_now_iso(),
        "contentUrl": info['video_path'],
        "keywords": info['seo_tags']
    }
    
    info['social_metadata'] = {
        "og:title": info['seo_title'],
        "og:description": info['seo_description'],
        "og:image": info['thumbnail']['file_path'],
        "og:video": info['video_path'],
        "twitter:card": "player",
        "twitter:title": info['seo_title'],
        "twitter:description": info['seo_description'],
        "twitter:image": info['thumbnail']['file_path']
    }
    
    info['category'] = next((v for k, v in info['categories'].items() if k in ' '.join(info['seo_tags']).lower()), 'General')
    
    info['uploader'] = {"name": info['uploader'],
                        "url": info['domain']}
    
    info['publication_date'] = get_time_now_iso()
    
    video = mp.VideoFileClip(info['video_path'])
    
    info['file_metadata'] = {
        'resolution': f"{video.w}x{video.h}",
        'format': 'MP4',
        'file_size_mb': os.path.getsize(info['video_path']) / (1024 * 1024)
    }
    
    video.close()
    videos_url = info.get('videos_url')
    video_id = info.get('video_id')
    canonical_url = f"{videos_url}/{video_id}"
    info['canonical_url']= canonical_url
    update_sitemap(info,
                   f"{info['parent_dir']}/../sitemap.xml")
    
    return info
