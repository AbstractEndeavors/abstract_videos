from .text_utils import *
from .audio_utils import *
from .seo_utils import *
from .ocr_utils import *
from .functions import *
from .audio_utils_clean import transcribe_audio_file_clean,transcribe_with_whisper_local
# Clear root logger handlers to prevent duplicate console output
logging.getLogger('').handlers.clear()
valid_keys =     ['parent_dir', 'video_path', 'info_directory', 'thumbnails_directory', 'info_path', 'filename', 'ext', 'remove_phrases', 'audio_path', 'video_json', 'categories', 'uploader', 'domain', 'videos_url', 'video_id', 'canonical_url', 'chunk_length_ms', 'chunk_length_diff', 'renew', 'whisper_result', 'video_text', 'keywords', 'combined_keywords', 'keyword_density', 'summary', 'seo_title', 'seo_description', 'seo_tags', 'thumbnail', 'duration_seconds', 'duration_formatted', 'captions_path', 'schema_markup', 'social_metadata', 'category', 'publication_date', 'file_metadata']

def update_json_data(json_data,update_data,keys=None):
    if keys == True:
        values_string = ''
        for key,value in update_data.items():
            values_string+= f"{key} == {value}\n"
        logger.info(f"new_datas:\n{values_string}")
        keys = valid_keys
    
    for key,value in update_data.items():
        if keys:
            if key in keys:
                json_data[key] = json_data.get(key) or value 
        else:
            json_data[key] = json_data.get(key) or value 
    return json_data
###json_data,chunk_length_ms=10000,renew=False
def transcribe_all_video_paths(directory=None,
                               output_dir=None,
                               remove_phrases=None,
                               summarizer=None,
                               kw_model=None,
                               generator=None,
                               LEDTokenizer=None,
                               LEDForConditionalGeneration=None,
                               uploader=None,
                               domain=None,
                               categories=None,
                               videos_url=None,
                               repository_dir=None,
                               directory_links=None,
                               videos_dir=None,
                               infos_dir=None,
                               base_url=None,
                               chunk_length_ms=None,
                               chunk_length_diff=None,
                               title=None,
                               renew=None,
                               remove_text=None,
                               video_id=None):
    logger.info(f"Entering transcribe_all_video_paths")
    directory = directory or os.getcwd()
    paths = glob.glob(path_join(directory, '**', '**'), recursive=True)
    paths = [file_path for file_path in paths if confirm_type(file_path,
                                                              media_types=get_media_types(['video']))]
    video_paths = get_all_file_types(directory=directory, types='video') or get_all_file_types(directory=directory, types='videos')
    for video_path in video_paths:
        transcribe_video_path(video_path=video_path,
                              output_dir=output_dir,
                              remove_phrases=remove_phrases,
                              summarizer=summarizer,
                              kw_model=kw_model,
                              generator=generator,
                              LEDTokenizer=LEDTokenizer,
                              LEDForConditionalGeneration=LEDForConditionalGeneration,
                              uploader=uploader,
                              domain=domain,
                              categories=categories,
                              videos_url=videos_url,
                              repository_dir=repository_dir,
                              directory_links=directory_links,
                              videos_dir=videos_dir,
                              infos_dir=infos_dir,
                              base_url=base_url,
                              chunk_length_ms=chunk_length_ms,
                              chunk_length_diff=chunk_length_diff,
                              title = title,
                              renew=renew,
                              remove_text=remove_text,
                              video_id=video_id)
    logger.info(f"Exiting transcribe_all_video_paths")

def transcribe_video_path(video_path,
                          output_dir=None,
                          remove_phrases=None,
                          summarizer=None,
                          kw_model=None,
                          generator=None,
                          LEDTokenizer=None,
                          LEDForConditionalGeneration=None,
                          uploader=None,
                          domain=None,
                          categories=None,
                          videos_url=None,
                          repository_dir=None,
                          directory_links=None,
                          videos_dir=None,
                          infos_dir=None,
                          base_url=None,
                          chunk_length_ms=None,
                          chunk_length_diff=None,
                          title=None,
                          renew=None,
                          remove_text=None,
                          video_id=None):
    remove_phrases = remove_phrases or []
    output_dir = output_dir if output_dir else make_dirs(directory, 'text_dir')
    logger.info(f"Processing video: {video_path}")
    info = get_info_data(video_path,
                         output_dir=output_dir,
                         remove_phrases=remove_phrases,
                         uploader=uploader,
                         domain=domain,
                         categories=categories,
                         videos_url=videos_url,
                         chunk_length_ms=chunk_length_ms,
                         chunk_length_diff=chunk_length_diff,
                         title=title,
                         renew=renew,
                         video_id=video_id)
    
    is_file = False
    audio_path = info.get('audio_path')
    if audio_path:
        is_file = os.path.isfile(audio_path)
    logger.info(f"audio_path is_file == {is_file}\n  audio_path == {video_path}")
    if not is_file:
        logger.info(f"function: extract_audio_from_video")
        extract_audio_from_video(video_path=info['video_path'],
                                 audio_path=info['audio_path'])

    whisper_result_bool = info.get("whisper_result") == None
    logger.info(f"whisper_result_bool == {whisper_result_bool}")
    if whisper_result_bool:
        logger.info(f"function: transcribe_with_whisper_local")
        info = transcribe_with_whisper_local(
                                            json_data=info,
                                            audio_path=info['audio_path'],
                                            model_size= "small",           # one of "tiny", "base", "small", "medium", "large"
                                            language='english')
    video_text_bool = info.get('video_text') == None
    logger.info(f"video_text_bool == {video_text_bool}")
    if video_text_bool:
        logger.info(f"function: analyze_video_text")
        info = analyze_video_text(video_path=info['video_path'],
                           output_dir=info['thumbnails_directory'],
                           json_data=info,
                           remove_phrases=info['remove_phrases'],
                           video_id=info['video_id'])

    combined_keywords_bool = info.get('combined_keywords')
    logger.info(f"combined_keywords_bool == {combined_keywords_bool}")
    if combined_keywords_bool:
        logger.info(f"function: get_text_and_keywords")
        whisper_result = info.get("whisper_result",{})
        full_text = whisper_result.get('text')
        info = refine_keywords(info.get("keywords"),
                               full_text,
                               info_data = info)
    summary_bool = info.get('summary') == None
    logger.info(f"summary_bool == {summary_bool}")
    if summary_bool:
        logger.info(f"function: get_summary")
        info = get_summary(info.get("full_text"),
                    keywords=info.get("keywords"),
                    json_data=info)
        
    seo_value_bool = info.get('seo_description') == None
    logger.info(f"seo_value_bool == {seo_value_bool}")
    if seo_value_bool:
        logger.info(f"function: get_seo_data")
        info = get_seo_data(info,
                            uploader=uploader,
                            domain=domain,
                            categories=categories,
                            videos_url=videos_url,
                            repository_dir=repository_dir,
                            directory_links=directory_links,
                            videos_dir=videos_dir,
                            infos_dir=infos_dir,
                            base_url=base_url,
                            generator=generator,
                            LEDTokenizer=LEDTokenizer,
                            LEDForConditionalGeneration=LEDForConditionalGeneration)
    safe_dump_to_file(data=info,
                      file_path=info['info_path'])
    return info

def get_info_data(video_path,
                  output_dir=None,
                  remove_phrases=None,
                  uploader=None,
                  domain=None,
                  categories=None,
                  videos_url=None,
                  chunk_length_ms=None,
                  chunk_length_diff=None,
                  title=None,
                  renew=None,
                  remove_text=None,
                  video_id=None):

    remove_phrases = remove_phrases or []
    remove_text = remove_text or False
    basename = os.path.basename(video_path)
    filename, ext = os.path.splitext(basename)
    video_id = video_id or filename.replace(' ', '-').lower()
    info_directory = make_dirs(output_dir, video_id)
    thumbnails_directory = make_dirs(info_directory, 'thumbnails')
    info_path = os.path.join(info_directory, 'info.json')
    info={}
    if os.path.isfile(info_path):
        logger.info(f"info_path: exists == {info_path}")
        info = safe_read_from_json(info_path)

    video_text_path = os.path.join(info_directory, 'video_text.json')
    audio_path = os.path.join(info_directory, 'audio.wav')
    video_json_path = os.path.join(info_directory, 'video_json.json')
    categories = categories or {'ai': 'Technology', 'cannabis': 'Health', 'elon musk': 'Business'}
    uploader = uploader or 'The Daily Dialectics'
    domain = domain or 'https://thedailydialectics.com'
    videos_url = videos_url or f"{domain}/videos"
    canonical_url = f"{videos_url}/{video_id}"
    chunk_length_ms = if_none_get_def(chunk_length_ms, 8000)
    chunk_length_diff = if_none_get_def(chunk_length_diff, -5)
    renew = if_none_get_def(renew, False)

    info['parent_dir']=output_dir
    info['video_path'] = video_path
    info['info_directory'] = info_directory
    info['thumbnails_directory']=thumbnails_directory
    info['info_path'] = info_path
    info['filename'] = video_id
    info['ext'] = ext
    info['title'] = title
    info['remove_phrases'] = remove_phrases
    info['audio_path'] = audio_path
    info['video_json'] = video_json_path
    info['categories'] = categories
    info['uploader'] = uploader
    info['domain'] = domain
    info['videos_url'] = videos_url
    info['video_id'] = video_id
    info['canonical_url'] = canonical_url
    info['chunk_length_ms'] = chunk_length_ms
    info['chunk_length_diff'] = chunk_length_diff
    info['renew'] = renew
        
    
        
    safe_dump_to_file(data=info, file_path=info.get('info_path'))
    return info
