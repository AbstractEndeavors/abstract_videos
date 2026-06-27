from .init_imports import *
import uuid
def generate_video_id(*args,**kwargs):
    return f"{uuid.uuid4().hex}"
def get_info_path_from_video_path(video_path):
    video_parts = get_file_parts(video_path)
    dirname = video_parts.get('dirname')
    return os.path.join(dirname,'info.json')
    
def get_media_id(url=None, video_id=None, video_path=None,registry_data=None):
    if url:
        video_id = get_video_id(url)
    if video_path and not video_id:
        info_path = get_info_path_from_video_path(video_path)
        if os.path.isfile(info_path):
            info_data = safe_load_from_json(info_path)
            video_id = info_data.get('id')
        elif registry_data:
            for vid_id,values in registry_data.items():
                vid_path = values.get('video_path')
                if os.path.isfile(vid_path) and vid_path == video_path:
                    return vid_id

    return video_id
def get_file_data(filepath, default=None):
    if not os.path.isfile(filepath):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        safe_dump_to_file(default or {}, filepath)
    return safe_read_from_file(file_path=filepath)

def load_json_keys(filepath, main_data=None, default=None):
    base = default or {}
    main = dict(main_data or {})
    try:
        disk = get_file_data(filepath, default=base)
        for k, v in (main or {}).items():
            if isinstance(v, dict):
                v.update(disk.get(k, {}))
            else:
                main[k] = disk.get(k, v)
        # Also merge any keys present on disk but missing in main
        for k, v in disk.items():
            main.setdefault(k, v)
        return main
    except Exception:
        return main or base
def _first_existing(*paths):
    for p in paths:
        if p and os.path.isdir(p):
            return p
    return None
