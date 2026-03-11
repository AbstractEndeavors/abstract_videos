#from .info_routes import *
#from .video_routes import *
#from .call_routes import *


from ..service_calls import *
from ..service_calls.text_tools.keybert_utils.keybert_manager import KeywordManager
from ..service_calls.text_tools.summarizer_utils.summarizer_manager import SummarizerManager
from ..service_calls.audio_tools.whisper_utils.whisper_manager import WhisperManager
from ..service_calls.video_tools.video_text_manager import VideoTextManager
from ..service_calls.info_utils.initial_info import get_initial_info_data
from ..service_calls.seo_utils.seo_manager import SEOManager
from abstract_flask import *
from abstract_utilities import get_all_file_types
from .route_vars import *
filepath = os.path.abspath(__file__)
service_calls_bp,logger = get_bp(filepath)
seo_mgr = SEOManager()
video_text_mgr = VideoTextManager()
kw_mgr = KeywordManager()
summ_mgr = SummarizerManager()
whisper_mgr = WhisperManager()

TEXT_DIR = "/var/www/typicallyoutliers/frontend/public/repository/text_dir"
VIDEOS_DIR = "/var/www/typicallyoutliers/frontend/public/repository/videos"
def get_all_available_videos(text_dir: str = TEXT_DIR) -> List[str]:
    """
    List all subdirectories in text_dir containing info.json.
    """
    return [p.name for p in Path(text_dir).iterdir() if p.is_dir() and (p / "info.json").is_file()]
@service_calls_bp.route('/get_available_raw_video_list', methods=['GET', 'POST'])
def getAvailableRawVideos():
    available_list = get_all_file_types('video',VIDEOS_DIR)
    return jsonify({"result":available_list})

@service_calls_bp.route("/extract_video_text", methods=["POST"])
def extract_video_text():
    req = request
    info = load_existing_info_for(req)
    updated = get_initial_info_data(req=req, info_data=info)
    return jsonify(updated)

@service_calls_bp.route("/extract_video_text", methods=["POST"])
def extract_video_text():
    req = request
    info = load_existing_info_for(req)
    updated = video_text_mgr.run(req=req, info_data=info)
    return jsonify(updated)

@service_calls_bp.route("/transcribe", methods=["POST"])
def transcribe():
    req = request
    info = load_existing_info_for(req)
    updated = whisper_mgr.run(req=req, info_data=info)
    return jsonify(updated)

@service_calls_bp.route("/generate_keywords", methods=["POST"])
def generate_keywords():
    req = request
    info = load_existing_info_for(req)
    new_info = kw_mgr.run(req=req, info_data=info)
    return jsonify(new_info)


@service_calls_bp.route("/generate_seo", methods=["POST"])
def generate_seo():
    req = request
    info = load_existing_info_for(req)
    updated = seo_mgr.run(req=req, info_data=info)
    return jsonify(updated)

@service_calls_bp.route("/generate_summary", methods=["POST"])
def generate_summary():
    req = request
    info = load_existing_info_for(req)
    updated = summ_mgr.run(req=req, info_data=info)
    return jsonify(updated)
