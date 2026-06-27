from .imports import *
from .registry import *
from .utils import *
def get_info_registry(
    config: StorageConfig=None,
    videos_root=None,
    documents_root=None,
    flat_layout: bool = False,
    **kwargs
    ):
    return infoRegistry(
        config=config,
        videos_root=videos_root,
        documents_root=documents_root,
        flat_layout= flat_layout,
        **kwargs
        )

def get_video_info(
    url=None, video_id=None, video_path=None,
    force_refresh=False, action=None,         # ← explicit, not via kwargs
    config: StorageConfig = None,
    videos_root=None, documents_root=None,
    flat_layout: bool = False,
    **kwargs,
):
    info_registry = infoRegistry(
        config=config, videos_root=videos_root,
        documents_root=documents_root, flat_layout=flat_layout,
        **kwargs,
    )
    return info_registry.get_video_info(
        url=url, video_id=video_id, video_path=video_path,
        force_refresh=force_refresh, action=action,    # ← forward
    )
def update_video_info(
    data,
    url=None,
    video_id=None,
    video_path=None,
    force_refresh=False,
    config: StorageConfig=None,
    videos_root=None,
    documents_root=None,
    flat_layout: bool = False,
    **kwargs
    ):
    info_registry = infoRegistry(
        config=config,
        videos_root=videos_root,
        documents_root=documents_root,
        flat_layout= flat_layout,
        **kwargs
        )
    info_registry.edit_info(data, video_id=video_id, url=url, video_path=video_path)


def extract_audio(
    url=None,
    video_id=None,
    video_path=None,
    force_refresh=False
    ):
    video_info = get_video_info(
        url=url,
        video_id=video_id,
        video_path=video_path,
        force_refresh=force_refresh,
        action="extract_audio")
    
    audio_path = video_info.get('audio_path')
    video_path = info.get('video_path')
    audio_path = os.path.join(video_dir,'audio.wav')

    extract_audio_from_video(video_path=video_path, audio_path=audio_path)
def get_analysis(
    text,
    scope=None,
    summary_preset=None,
    keyword_preset=None,
    input_policy=None
    ):
    scope='page'
    summary_preset= summary_preset or "article"
    keyword_preset= keyword_preset or "seo"
    input_policy=input_policy or "allow"
    return analyze_media_text(
        text,
        scope=scope,
        summary_preset=summary_preset,
        keyword_preset=keyword_preset,
        input_policy=input_policy
    )
def assure_video_download_refresh(video_info,url=None):
    video_path = video_info.get('video_path')
    info_path = video_info.get('info_path')
    if url and os.path.isfile(video_path):
        os.remove(video_path)
    if os.path.isfile(info_path):
        os.remove(info_path)
def assure_video_download(
    url=None,
    video_id=None,
    video_path=None,
    force_refresh=False
    ):
    video_info = get_video_info(
        url=url,
        video_id=video_id,
        video_path=video_path,
        force_refresh=force_refresh,
        action="video_download")
    download=False
    video_path = video_info.get('video_path')
    info_path = video_info.get('info_path')
    video_dir = video_info.get('video_dir')
    video_basename = video_info.get('basename')
    if force_refresh:
        assure_video_download_refresh(
            video_info=video_info,
            url=url
            )
    if not os.path.isfile(video_path):
        info = for_dl_video(url,download_directory=video_dir,video_basename=video_basename)
        safe_dump_to_json(data=info,file_path=info_path)
        if os.path.isfile(info_path) or os.path.isfile(video_path):
            if os.path.isfile(video_path):
                video_info['checklist']["info"]=True
            if os.path.isfile(video_path):
                video_info['checklist']["download"]=True
            update_video_info(video_info,url=url,
                                video_id=video_id,
                                video_path=video_path)
    if force_refresh and os.path.isfile(info_path):
        os.remove(info_path)            
    if not os.path.isfile(info_path):
        info = for_dl_video(url,download_directory=video_dir,output_filename=video_basename,download=download)
        safe_dump_to_json(data=info,file_path=info_path)
        video_info['checklist']["info"]=True
        update_video_info(video_info,
                          url=url,
                          video_id=video_id,
                          video_path=video_path
                          )
    return video_info
def assure_audio_refresh(video_info):
    audio_path = video_info.get('audio_path')
    if os.path.isfile(audio_path):
        os.remove(audio_path)

def assure_audio(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):

    video_info = assure_video_download(
        url=url,
        video_id=video_id,
        video_path=video_path,
        force_refresh=force_refresh)
    
    audio_path = video_info.get('audio_path')
    video_path = video_info.get('video_path')
    if force_refresh:
        assure_audio_refresh(video_info)
    if not os.path.isfile(audio_path):
        extract_audio_from_video(video_path=video_path, audio_path=audio_path)
        if os.path.isfile(audio_path):
            video_info['checklist']["audio"]=True
            update_video_info(video_info,
                          url=url,
                          video_id=video_id,
                          video_path=video_path
                          )
    return video_info
def assure_video_thumbnails_refresh(video_info):
    thumbnails_dir = video_info.get('thumbnails_dir')
    if os.path.isdir(thumbnails_dir):
        shutil.rmtree(thumbnails_dir)
def assure_video_thumbnails(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):

    video_info = assure_video_download(
        url=url,
        video_id=video_id,
        video_path=video_path,
        force_refresh=force_refresh)
    thumbnails_dir = video_info.get('thumbnails_dir')
    if force_refresh:
        assure_video_thumbnails_refresh(video_info)
    info_path = video_info.get('info_path')
    video_dir = video_info.get('video_dir')
    if not os.path.isdir(thumbnails_dir) or len(os.listdir(thumbnails_dir)) == 0:
        info = safe_load_from_json(info_path)
        get_thumbnails(video_dir,info)
        if os.path.isdir(thumbnails_dir) and len(os.listdir(thumbnails_dir)) != 0:
            video_info['checklist']["thumbnails"]=True
            update_video_info(video_info,
                              url=url,
                              video_id=video_id,
                              video_path=video_path
                              )
    return video_info
def assure_video_transcription_refresh(video_info):
    whisper_path = video_info.get('whisper_path')
    if os.path.isdir(whisper_path):
        os.remove(whisper_path)
def assure_video_transcription(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):

    video_info = assure_audio(
        url=url,
        video_id=video_id,
        video_path=video_path,
        force_refresh=force_refresh)
    audio_path = video_info.get('audio_path')
    whisper_path = video_info.get('whisper_path')
    if force_refresh:
        assure_video_transcription_refresh(video_info)
    if not os.path.isfile(whisper_path):
        whisper_data = whisper_transcribe(audio_path=audio_path)
        if whisper_data:
            safe_dump_to_json(data=whisper_data,file_path=whisper_path)
            if os.path.isfile(whisper_path):
                video_info['checklist']["whisper"]=True
                update_video_info(video_info,
                              url=url,
                              video_id=video_id,
                              video_path=video_path
                              )
    return video_info
def assure_video_metadata_refresh(video_info):
    metadata_path = video_info.get('metadata_path')
    if os.path.isdir(metadata_path):
        os.remove(metadata_path)
def assure_video_metadata(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):

    video_info = assure_video_transcription(
        url=url,
        video_id=video_id,
        video_path=video_path,
        force_refresh=force_refresh)
    whisper_path = video_info.get('whisper_path')
    metadata_path = video_info.get('metadata_path')
    if force_refresh:
        assure_video_metadata_refresh(video_info)
    if os.path.isfile(whisper_path) and not os.path.isfile(metadata_path):
        whisper_data = safe_load_from_json(whisper_path)
        if whisper_data:
            whisper_text = whisper_data.get('text')
            if whisper_text:
                metadata = get_analysis(whisper_text)
                if metadata:
                    metadata = metadata.to_dict()
                    safe_dump_to_json(data=metadata,file_path=metadata_path)
                    if os.path.isfile(metadata_path):
                        video_info['checklist']["metadata"]=True
                        update_video_info(video_info,
                                      url=url,
                                      video_id=video_id,
                                      video_path=video_path
                                      )
    return video_info
def assure_video_seodata_refresh(video_info):
    seodata_path = video_info.get('seodata_path')
    if os.path.isdir(seodata_path):
        os.remove(seodata_path)
def assure_video_seodata(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):

    video_info = assure_video_metadata(
            url=url,
            video_id=video_id,
            video_path=video_path,
            force_refresh=force_refresh)
    seodata_path = video_info.get('seodata_path')
    if force_refresh:
        assure_video_seodata_refresh(video_info)
    if not os.path.isfile(seodata_path):
        config = SiteConfig.from_env()
        DOMAIN = config.domain
        info_data["metadata"]=metadata
        href = f"{DOMAIN}/video/{video_id}"
        title = info.get('title')
        summary = metadata.get('summary')
        hashtags = metadata.get('keywords').get('hashtags')
        meta_keywords = metadata.get('keywords').get('meta_keywords')
        optimal_thumbnail = pick_optimal_thumbnail(transcription,meta_keywords,thumbnail_paths=thumbnails,directory=video_dir)
        
        page_data = get_page_data(
            title=title,
            href=href,
            summary=summary,
            keywords=meta_keywords.replace(', ',',').split(','),
            keywords_str=meta_keywords,
            thumbnail=optimal_thumbnail or thumbnails[0])
        safe_dump_to_json(data=page_data,file_path=seodata_path)
        video_info['checklist']["seodata"]=True
        update_video_info(video_info,
                                      url=url,
                                      video_id=video_id,
                                      video_path=video_path
                                      )
    return video_info
def get_video_download(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):
    video_info = assure_video_download(
            url=url,
            video_id=video_id,
            video_path=video_path,
            force_refresh=force_refresh)
    info_path = video_info.get('info_path')
    return safe_load_from_json(info_path)
def get_video_audio(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):
    video_info = assure_audio(
            url=url,
            video_id=video_id,
            video_path=video_path,
            force_refresh=force_refresh)
    return video_info.get('audio_path')
def get_video_thumbnails(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):
    video_info = assure_video_thumbnails(
            url=url,
            video_id=video_id,
            video_path=video_path,
            force_refresh=force_refresh)
    thumbnails_dir = video_info.get('thumbnails_dir')
    return [os.path.join(thumbnails_dir,item) for item in os.listdir(thumbnails_dir) if item]
def get_video_transcription(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):
    video_info = assure_video_transcription(
            url=url,
            video_id=video_id,
            video_path=video_path,
            force_refresh=force_refresh)
    whisper_path = video_info.get('whisper_path')
    return safe_load_from_json(whisper_path)
def get_video_metadata(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):
    video_info = assure_video_metadata(
            url=url,
            video_id=video_id,
            video_path=video_path,
            force_refresh=force_refresh)
    metadata_path = video_info.get('metadata_path')
    return safe_load_from_json(metadata_path)
def get_video_seodata(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):
    video_info = assure_video_metadata(
            url=url,
            video_id=video_id,
            video_path=video_path,
            force_refresh=force_refresh)
    seodata_path = video_info.get('seodata_path')
    return safe_load_from_json(seodata_path)
def get_all(
        url=None,
        video_id=None,
        video_path=None,
        force_refresh=False
        ):
    info_data = get_video_info(
                url=url,
                video_id=video_id,
                video_path=video_path,
                force_refresh=force_refresh,
                action="get_all")

    info = get_video_download(
                url=url,
                video_id=video_id,
                video_path=video_path,
                force_refresh=force_refresh)
    info_data['video_info'] = info
    video_id = info_data.get('video_id')
    video_path = info_data.get('video_path')
    video_dir = info_data.get('video_dir')
    info_path = info_data.get('info_path')
    thumbnails = get_video_thumbnails(
                url=url,
                video_id=video_id,
                video_path=video_path,
                force_refresh=force_refresh)
    info_data["thumbnail_paths"]=thumbnails
    transcription = get_video_transcription(
                url=url,
                video_id=video_id,
                video_path=video_path,
                force_refresh=force_refresh)
    info_data["transcription"]=transcription
    metadata = get_video_metadata(
                url=url,
                video_id=video_id,
                video_path=video_path,
                force_refresh=force_refresh)
    info_data["metadata"]=metadata
    seodata = get_video_seodata(
                url=url,
                video_id=video_id,
                video_path=video_path,
                force_refresh=force_refresh)
    info_data["seodata"]=seodata
    return info_data
