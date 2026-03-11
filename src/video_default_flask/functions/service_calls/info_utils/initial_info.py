from ..routes import *
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

    vp = new_data['video_path']
    ap = new_data['audio_path']
    td = new_data['thumbnails_directory']
    
    # 2) Ensure audio exists
    if vp and ap and not os.path.isfile(ap):
        result = extract_audio_from_video(video_path=vp, audio_path=ap)
        if result:
            info_data['audio_path'] = ap

    # 3) Ensure at least one thumbnail exists
    #    (you’ll need to write your own create_thumbnails helper)
    if vp and td and not any(os.scandir(td)):
        thumbs = create_thumbnails(video_path=vp, output_dir=td)
        # e.g. create_thumbnails returns a list of file‐paths
        info_data['thumbnails'] = thumbs
    input(info_data)
    # 4) Persist your updates back into info.json
    safe_save_updated_json_data(
        data={'audio_path': info_data.get('audio_path'),
              'thumbnails': info_data.get('thumbnails', [])},
        file_path=get_video_info_path(**info_data),
        valid_keys=['audio_path', 'thumbnails'],
        invalid_keys=[]
    )

    return info_data
