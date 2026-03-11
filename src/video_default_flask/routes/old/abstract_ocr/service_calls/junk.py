from .functions import update_json_data,execute_if_bool,generate_file_id
from .variable_utils import *
from .video_utils import extract_audio_from_video,analyze_video_text
from .audio_utils import transcribe_with_whisper_local
from .text_utils import refine_keywords,get_summary
from .seo_utils import get_seo_data
def make_list_it(obj=None):
    obj = make_list(obj or [])
    return obj
def remove_directory(directory,paths=None):
    paths = make_list_it(paths)
    shutil.rmtree(audio_dir)
    for path in paths:
        remove_path(path=path)
def remove_path(path=None):
    if path and os.path.exists(path):
        if os.path.isdir(path):
            remove_directory(path)
        else:
            os.remove(path)
