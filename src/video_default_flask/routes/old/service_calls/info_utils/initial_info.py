from ..routes import *
from abstract_ocr import extract_audio_from_video
from ..video_tools import analyze_video_text

REMOVE_PHRASES = ['Video Converter', 'eeso', 'Auseesott', 'Aeseesott', 'esoft']

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
