from .route_vars import *
from abstract_utilities import get_all_file_types
from .abstract_ocr import get_video_info_data,get_video_info_data,get_video_info_path,get_videos_path
filepath = os.path.abspath(__file__)
call_routes_bp,logger = get_bp(filepath)
TEXT_DIR = "/var/www/typicallyoutliers/frontend/public/repository/text_dir"
VIDEOS_DIR = "/var/www/typicallyoutliers/frontend/public/repository/videos"
def get_all_available_videos(text_dir: str = TEXT_DIR) -> List[str]:
    """
    List all subdirectories in text_dir containing info.json.
    """
    return [p.name for p in Path(text_dir).iterdir() if p.is_dir() and (p / "info.json").is_file()]
@call_routes_bp.route('/get_available_raw_video_list', methods=['GET', 'POST'])
def getAvailableRawVideos():
    available_list = get_all_file_types('video',VIDEOS_DIR)
    return jsonify({"result":available_list})
