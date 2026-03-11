from ..routes import *

from abstract_utilities import (os,
                                safe_save_updated_json_data,
                                get_result_from_data,
                                remove_path,
                                remove_directory,
                                make_list_it,)
from abstract_ocr.ocr_utils import extract_text_from_image,cv2

from .video_text_manager import VideoTextManager

video_text_mgr = VideoTextManager()

@app.route("/extract_video_text", methods=["POST"])
def extract_video_text():
    req = request
    info = load_existing_info_for(req)
    updated = video_text_mgr.run(req=req, info_data=info)
    return jsonify(updated)
