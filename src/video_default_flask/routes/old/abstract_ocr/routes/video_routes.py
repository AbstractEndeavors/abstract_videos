from .route_vars import *
from abstract_utilities import get_all_file_types

from .abstract_ocr import get_video_info_data,get_video_info_data,get_video_info_path,get_videos_path
filepath = os.path.abspath(__file__)
video_routes_bp,logger = get_bp(filepath)
TEXT_DIR = "/var/www/typicallyoutliers/frontend/public/repository/text_dir"
VIDEOS_DIR = "/var/www/typicallyoutliers/frontend/public/repository/videos"
def get_all_available_videos(text_dir: str = TEXT_DIR) -> List[str]:
    """
    List all subdirectories in text_dir containing info.json.
    """
    return [p.name for p in Path(text_dir).iterdir() if p.is_dir() and (p / "info.json").is_file()]
@video_routes_bp.route('/get_available_raw_video_list', methods=['GET', 'POST'])
def getAvailableRawVideos():
    available_list = get_all_file_types('video',VIDEOS_DIR)
    return jsonify({"result":available_list})

@video_routes_bp.route('/get_available_video_list', methods=['GET', 'POST'])
def getAvailableVideos():
    available_list = get_all_available_videos()
    return jsonify({"result":available_list})

@video_routes_bp.route('/get_available_video_info', methods=['GET', 'POST'])
def getAvailableVideosInfo():
    all_infos = []
    available_list = get_all_available_videos()

    for video_id in available_list:
       
            video_data = get_video_info_data(video_id=video_id)
            all_infos.append(video_data)

    return jsonify({"result":all_infos}), 200

@video_routes_bp.route('/video_info', methods=['GET', 'POST'])
def getVideoInfo():
   
        data,info_data = get_request_info_data(request)
        video_id = data.get('video_id')
        if not video_id:
            return jsonify({"error": "No video_id provided"}), 400
        
            info_data = get_video_info_data(video_id=video_id)
            if not info_data:
                return jsonify({"error": f"No info_data from provided video_id: {video_id} with path: {get_video_info_path(video_id)}"}), 400
            logger.error(f"video_id: {video_id}")
            video_data = get_video_info_data(video_id=video_id,info_data=info_data)
            return jsonify({"result":video_data}), 200
  

