from .route_vars import *
filepath = os.path.abspath(__file__)
info_routes_bp,logger = get_bp(filepath)
from .abstract_ocr.functions import (get_initial_info_data,
                                     get_seo_data_call)
from .abstract_ocr.functions.execute_utils import (execute_summarizer_call,
                                                   execute_keywords_call,
                                                   execute_whisper_call,
                                                   execute_video_text_call,
                                                   extract_audio_from_video_call)
from .abstract_ocr.functions import *

def get_all_info_data_call(**info_data):
    
    info_data = get_initial_info_data(**info_data)
    info_data = extract_audio_from_video_call(info_data = info_data)
    info_data = execute_video_text_call(info_data = info_data)
    info_data = execute_whisper_call(info_data = info_data)
    
    info_data = execute_keywords_call(info_data = info_data)
    info_data = execute_summarizer_call(info_data = info_data)
    info_data = get_seo_data_call(info_data = info_data)
    return info_data
@info_routes_bp.route("/get_initial_info_data", methods=['POST', 'GET'])
def getInitialInfo():
    info_data = get_initial_info_data(request)
    return jsonify({"result":info_data}), 200
@info_routes_bp.route("/extract_audio_from_video", methods=['POST', 'GET'])
def extractAudioFromVideo():
    info_data = extract_audio_from_video_call(request)
    return jsonify({"result":info_data}), 200

@info_routes_bp.route("/transcribe_with_whisper_local", methods=['POST', 'GET'])
def transcribeWithWhisperLocal():
    info_data =execute_whisper_call(request)
    return jsonify({"result":info_data}), 200

@info_routes_bp.route("/analyze_video_text", methods=['POST', 'GET'])
def analyzeVideoText():
    info_data = execute_video_text_call(request)
    return jsonify({"result":info_data}), 200

@info_routes_bp.route("/refine_keywords", methods=['POST', 'GET'])
def refineKeywords():
    info_data = execute_keywords_call(request)
    return jsonify({"result":info_data}), 200


@info_routes_bp.route("/get_video_seo_data", methods=['POST', 'GET'])
def getSeoData():
    info_data = get_seo_data_call(request)
    return jsonify({"result":info_data}), 200

        
    
@info_routes_bp.route("/get_videos_infos_datas", methods=['POST', 'GET'])
def getInfosDatas():
    data,info_data = get_request_info_data(request)
    video_path = data.get('video_path')
    infos_datas = get_videos_infos(directory = directory, info_data = info_data)
    return jsonify({"result":info_data}), 200

@info_routes_bp.route("/get_video_info_data", methods=['POST', 'GET'])
def getInfoData():
    data,info_data = get_request_info_data(request)
    info_data = get_video_info_data(**data)
    return jsonify({"result":info_data}), 200

@info_routes_bp.route("/get_video_info_path", methods=['POST', 'GET'])
def getInfoPath():
    data,info_data = get_request_info_data(request)
    info_path = get_video_info_path(**data)
    return jsonify({"result":info_path}), 200


@info_routes_bp.route("/get_video_info_dir", methods=['POST', 'GET'])
def getVideoInfoDir():
    data,info_data = get_request_info_data(request)
    info_dir = get_video_info_dir(**data)
    return jsonify({"result":info_dir}), 200

@info_routes_bp.route("/get_video_id", methods=['POST', 'GET'])
def getVideoId():
    data,info_data = get_request_info_data(request)
    video_id = get_video_id(**data)
    return jsonify({"result":video_id}), 200

@info_routes_bp.route("/get_video_basename", methods=['POST', 'GET'])
def getVideoBasename():
    data,info_data = get_request_info_data(request)
    basename = get_video_basename(**data)
    return jsonify({"result":basename}), 200


@info_routes_bp.route("/get_thumbnails_dir", methods=['POST', 'GET'])
def getThumbnailsDir():
    data,info_data = get_request_info_data(request)
    thumbnails_dir = get_thumbnails_dir(**data)
    return jsonify({"result":thumbnails_dir}), 200

@info_routes_bp.route("/get_all_info_data_call", methods=['POST', 'GET'])
def getAllInfoDataCallApi():
    data,info_data = get_request_info_data(request)
    info_data = get_all_info_data_call(video_path=data.get('video_path'))
    return jsonify({"result":info_data}), 200

def find_delete_whisper(key,info_data,info_path,data,data_path):
    data_data = info_data.get(key)
    if data_data:
        data[key]=data_data
        safe_dump_to_file(data=data,file_path=data_path)
        del info_data[key]
        safe_dump_to_file(data=info_data,file_path=info_path)
    return info_data,data

@info_routes_bp.route("/split_info_data", methods=['POST', 'GET'])
def getAllInfoataCallApi():
    data,info_data = get_request_info_data(request)
    info_dir = get_video_info_dir(**data)
    info_data = get_video_info_data(**data)
    info_path = os.path.join(info_dir,'info.json')
    whisper_result_path = os.path.join(info_dir, 'whisper_result.json')
    if not os.path.exists(whisper_result_path):
        safe_dump_to_file(data={},file_path=whisper_result_path)
    whisper_data = safe_read_from_json(whisper_result_path)
    info_data,whisper_data = find_delete_whisper('whisper_result',info_data,info_path,whisper_data,whisper_result_path)
    info_data,whisper_data = find_delete_whisper('segments',info_data,info_path,whisper_data,whisper_result_path)
    info_data,whisper_data = find_delete_whisper('text',info_data,info_path,whisper_data,whisper_result_path)
    info_data,whisper_data = find_delete_whisper('language',info_data,info_path,whisper_data,whisper_result_path)

    return jsonify({"result":info_data}), 200
@info_routes_bp.route("/get_all_info_data_call", methods=['POST', 'GET'])
def getAllInfoDataCallALL():
    data,info_data = get_request_info_data(request)
    info_data = get_all_info_data_call(**info_data)
    return jsonify({"result":info_data}), 200
