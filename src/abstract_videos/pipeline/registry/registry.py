from .imports import *
import uuid
PURGE_TARGETS: dict[str, tuple[str, ...]] = {
    "get_all":         ("audio_path", "thumbnails_dir", "whisper_path",
                        "metadata_path", "seodata_path", "info_path",
                        "video_path"),
    "video_download":  ("video_path", "info_path"),
    "extract_audio":   ("audio_path",),
    "thumbnails":      ("thumbnails_dir",),
    "transcribe":      ("whisper_path",),
    "metadata":        ("metadata_path",),
    "seodata":         ("seodata_path",),
}

def _purge(values: dict, keys: tuple[str, ...]) -> None:
    for k in keys:
        p = values.get(k)
        if not p or not os.path.exists(p):
            continue
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)


def generate_video_id(*args,**kwargs):
    return f"{uuid.uuid4().hex}"
def get_registry_data(config):
    registry_path = config.registry_path
    return safe_load_from_json(registry_path)
def search_config_for_id(config,url=None, video_id=None, video_path=None):
    url = get_corrected_url(url)
    
    registry_data = get_registry_data(config)
    
    if video_id and registry_data.get(video_id):
        return video_id
    for video_id,values in registry_data.items():
        if (url and url == values.get('url')) or (video_path and values.get('video_path') and video_path == values.get('video_path')):
            return video_id

    return get_media_id(url=url, video_id=video_id, video_path=video_path,registry_data=registry_data)     
def get_video_record(config,url=None, video_id=None, video_path=None, force_refresh=False, hide_audio=False,move_video=False,action = None):
    video_id = search_config_for_id(
        config,
        url=url,
        video_id=video_id,
        video_path=video_path
        )
    registry_data= get_registry_data(config)
    values = registry_data.get(video_id)
    # registry.py.get_video_record — purge block
    # inside get_video_record:
    if force_refresh and values and action:
        targets = PURGE_TARGETS.get(action)
        if targets is None:
            raise ValueError(f"Unknown action for force_refresh: {action!r}")
        _purge(values, targets)
        # if the purge wiped video_path or info_path, rebuild values; else keep
        if "video_path" in targets or action == "get_all":
            values = None
    elif values:
        return values                          # ← force rebuild of values dict

        




    if video_path:
        dirname = os.path.dirname(video_path)
        basename = os.path.basename(video_path)
        filename,ext= os.path.splitext(basename)
        if move_video:
            video_dir = os.path.join(config.videos_root,video_id)
            os.makedirs(video_dir,exist_ok=True)
            nu_video_path = os.path.join(video_dir,basename)
            shutil.move(video_path,nu_video_path)
                    
        else:
            video_dir = dirname
        
    else:
        logger.info(video_id)
        logger.info(config.videos_root)
        video_dir = os.path.join(config.videos_root,video_id)
        filename= 'video'
        ext='.mp4'
        basename = f"{filename}{ext}"
    video_path = os.path.join(video_dir,basename)
    os.makedirs(video_dir,exist_ok=True)
    
    info_path = os.path.join(video_dir,'info.json')
    audio_path = os.path.join(video_dir,'audio.wav')
    thumbnails_dir = os.path.join(video_dir,'thumbnails')
    audio_path = os.path.join(video_dir,'audio.wav')
    whisper_path = os.path.join(video_dir,'whisper.json')
    metadata_path = os.path.join(video_dir,'metadata.json')
    seodata_path = os.path.join(video_dir,'seodata.json')

    values = {
        "video_id":video_id,
        "url":url,
        "basename":basename,
        "ext":ext,
        "filename":filename,
        "info_path":info_path,
        "video_path":video_path,
        "video_dir":video_dir,
        "audio_path":audio_path,
        "thumbnails_dir":thumbnails_dir,
        "whisper_path":whisper_path,
        "metadata_path":metadata_path,
        "seodata_path":seodata_path,
        "checklist":{
            "download":False,
            "info":False,
            "thumbnails":False,
            "audio":False,
            "whisper":False,
            "metadata":False,
            "seodata":False
            }
        }
  
    
    return values
def _save_registry_unlocked(self):
    # Caller holds write_lock (thread-safety); now add process-safety.
    tmp = f"{self.registry_path}.tmp"
    safe_dump_to_file(self.registry, tmp)
    # atomic replace still helps, but lock ensures we don't interleave writers
    with open(self.registry_path, "wb") as f:
        portalocker.lock(f, portalocker.LOCK_EX)
        with open(tmp, "rb") as src:
            f.write(src.read())
        f.flush()
        os.fsync(f.fileno())
        portalocker.unlock(f)
    os.remove(tmp)
def _write_registry(config, video_id, data):
    """Atomic write to flat JSON registry — never leaves a partial file."""
    registry_path = config.registry_path
    registry_dir = os.path.dirname(registry_path)
    registry_data = safe_load_from_json(registry_path) or {}
    registry_data[video_id] = data
    
    fd, tmp_path = tempfile.mkstemp(dir=registry_dir, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(registry_data, f, indent=2)
        os.replace(tmp_path, registry_path)  # atomic on POSIX, best-effort on Windows
    except Exception as e:
        os.unlink(tmp_path)
        raise
class infoRegistry(metaclass=SingletonMeta):
    def __init__(self, config: StorageConfig = None, videos_root=None, documents_root=None, flat_layout: bool = False,override=False, **kwargs):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.config = config or StorageConfig.from_env()
            self.videos_root = self.config.videos_root
            self.documents_root = self.config.documents_root
            self.registry_path = self.config.registry_path
            if not os.path.isfile(self.registry_path):
                safe_dump_to_json(data={}, file_path=self.registry_path)
            self.db_available = init_db()

    def _upsert(self, video_id, data: dict):
        _write_registry(self.config, video_id, data)
        if self.db_available:
            try:
                upsert_video(video_id, info=data)
            except Exception as e:
                log.debug("DB upsert skipped for %s: %s", video_id, e)

    def get_video_info(self, url=None, video_id=None, video_path=None,
                       force_refresh=False, action=None):
        values = get_video_record(
            self.config, url=url, video_id=video_id, video_path=video_path,
            force_refresh=force_refresh, hide_audio=False, action=action,
        )
        self._upsert(values["video_id"], values)   # ← from values, not param
        return values
    def edit_info(self, data, video_id=None, url=None, video_path=None):
        if not video_id:
            video_id = get_video_id(url) if url else generate_video_id(video_path)
        self._upsert(video_id, data)
        return self.get_video_info(video_id=video_id, force_refresh=True)
