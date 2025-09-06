from abstract_ocr.text_utils import *
from abstract_ocr.audio_utils import *
from abstract_ocr.video_utils import *
from abstract_ocr.functions import (logger,
                        create_key_value,
                        os,
                        timestamp_to_milliseconds,
                        format_timestamp,
                        get_time_now_iso,
                        parse_timestamp,
                        url_join,
                        get_from_list,
                        quote,
                        datetime,
                        update_sitemap)
from abstract_utilities import *
from .routes import *
def get_whisper_result_data(**kwargs):
    whisper_result_path = kwargs.get('whisper_result_path')
    if whisper_result_path:
        return safe_load_from_file(whisper_result_path)
        
    

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

def get_seo_title(title=None,keywords=None,filename=None,title_length=None,description=None):
    title_length =title_length or 70
    primary_keyword = filename
    if keywords and len(keywords)>0:
        primary_keyword = keywords[0]
    seo_title = f"{primary_keyword} - {title}"
    seo_title = get_from_list(seo_title,length=title_length)
    return seo_title
def get_seo_description(description=None,keywords=None,keyword_length=None,desc_length=None):
    keyword_length = keyword_length or 3
    desc_length=desc_length or 300
    seo_desc = f"{description} Explore {keywords}"
    seo_description = get_from_list(seo_desc,length=desc_length)
    return seo_description
def get_title_tags_description(title=None,keywords=None,summary=None,filename = None,title_length = None,summary_length=None,keyword_length=None,desc_length=None,description=None):
    summary_length = summary_length or 150
    keyword_length = keyword_length or 3
    summary_desc = get_from_list(description,length=summary_length)
    keywords_str=''
    seo_title = get_seo_title(title=title,keywords=keywords,filename=filename,title_length=title_length,description=description)
    if isinstance(keywords,list):
        keywords = get_from_list(keywords,length=keyword_length)
        if keywords and len(keywords)>0 and isinstance(keywords[0],list):
            keywords = keywords[0]
        if keywords:
            keywords_str = ', '.join(keywords)
    seo_description = eatAllQuotes(get_seo_description(summary_desc,keywords_str,keyword_length=keyword_length,desc_length=desc_length))
    seo_tags = [kw for kw in keywords if kw.lower() not in ['video','audio','file']]
    return seo_title,keywords_str,seo_description,seo_tags
def get_seo_data(info_data=None,
                 uploader=None,
                 domain=None,
                 categories=None,
                 videos_url=None,
                 repository_dir=None,
                 directory_links=None,
                 videos_dir=None,
                 infos_dir=None,
                 base_url=None,
                 generator=None,
                 LEDTokenizer=None,
                 LEDForConditionalGeneration=None):
    info = info_data or {}
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
    for keyword_key in ['combined_keywords','keywords']:
        keywords = info.get(keyword_key,[])
        if keywords and len(keywords)>0:
            if isinstance(keywords,dict):
                keywords = keywords[list(keywords.values())[0]]
            break
    filename = info.get('filename')
    if not filename:
        basename = os.path.basename(video_path)
        filename,ext = os.path.splitext(basename)
        info['basename'] = basename
        info['filename'] = filename
    title = info.get('title',filename)
    info['title']=title
    summary = info.get('summary','')
    description = info.get('description','')
    seo_title,keywords_str,seo_description,seo_tags = get_title_tags_description(title=title,
                                                                                 keywords=keywords,
                                                                                 summary=summary,
                                                                                 filename=filename,
                                                                                 description=description)
    info['seo_title'] = seo_title
    info['seo_description'] = seo_description
    info['seo_tags'] = seo_tags
    video_text = info.get('video_text')
    thumbnail_directory = info['thumbnails_directory']
    thumbnail_list = os.listdir(thumbnail_directory)
    thumbnail_basename = thumbnail_list[0]
    thumbnail_filepath = os.path.join(thumbnail_directory,thumbnail_basename)
    thumbnail_filename,thumbnail_ext = os.path.splitext(thumbnail_basename)
    info['thumbnail']={"file_path":thumbnail_filepath,"alt_text":thumbnail_filename}
    

    if video_text and len(video_text)>0:
        thumnail_data = video_text[0]
        thumbnail_filepath = os.path.join(info['thumbnails_directory'],thumnail_data.get("frame"))
        info['thumbnail']['file_path'] = thumbnail_filepath
        
        thumbnail_alt_text = thumnail_data.get("text")
        info['thumbnail']['alt_text']= thumbnail_alt_text
        
    whisper_json = get_whisper_result_data(**info)
    if whisper_json.get('segments'):
        thumbnail_score = pick_optimal_thumbnail(whisper_json,keywords,info["thumbnails_directory"],info=info)
        if thumbnail_score:
            best_frame, score, matched_text = thumbnail_score
            file_path = os.path.join(info['thumbnails_directory'],best_frame)
            info['thumbnail']['file_path']= file_path
            alt_text = get_from_list(matched_text,length=100)
            info['thumbnail']['alt_text']= alt_text
    file_path = info['thumbnail'].get('file_path')
    if file_path=='dont you fucking do it':
        basename = os.path.basename(file_path)
        filename,ext = os.path.splitext(basename)
        alt_text = info['thumbnail'].get('alt_text')
        if alt_text:
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
    

    
    duration_seconds,duration_formatted = get_audio_duration(info['audio_path'])
    info['duration_seconds'] = duration_seconds
    info['duration_formatted'] = duration_formatted
    export_srt_whisper(
        whisper_json,
        os.path.join(info["info_dir"], "captions.srt")
    )
    
    info['captions_path'] = os.path.join(info['info_dir'],
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
##    
    info['publication_date'] = get_time_now_iso()
    
    info['video_metadata'] = get_video_metadata(info['video_path'])
    info['canonical_url'] = info.get('canonical_url') or domain
    update_sitemap(info,
                   f"{os.path.dirname(info['info_dir'])}/../sitemap.xml")
    
    return info
