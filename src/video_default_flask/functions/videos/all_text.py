from .route_vars import *
filepath = os.path.abspath(__file__)
call_routes_bp,logger = get_bp(filepath)
from ..functions.videos.video_utils import *

@call_routes_bp.route('/generate_media_url', methods=['GET', 'POST'])
def GenerateMediaUrl():
        data,info_data = get_request_info_data(request)
        result = generate_media_url(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_link', methods=['GET', 'POST'])
def GetLink():
        data,info_data = get_request_info_data(request)
        result = get_link(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/generate_video_id', methods=['GET', 'POST'])
def GenerateVideoId():
        data,info_data = get_request_info_data(request)
        result = generate_video_id(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_file_size', methods=['GET', 'POST'])
def GetFileSize():
        data,info_data = get_request_info_data(request)
        result = get_file_size(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_image_metadata', methods=['GET', 'POST'])
def GetImageMetadata():
        data,info_data = get_request_info_data(request)
        result = get_image_metadata(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/extract_video_metadata', methods=['GET', 'POST'])
def ExtractVideoMetadata():
        data,info_data = get_request_info_data(request)
        result = extract_video_metadata(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_item_from_info', methods=['GET', 'POST'])
def GetItemFromInfo():
        data,info_data = get_request_info_data(request)
        result = get_item_from_info(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_all_available_videos', methods=['GET', 'POST'])
def GetAllAvailableVideos():
        data,info_data = get_request_info_data(request)
        result = get_all_available_videos(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_info_path', methods=['GET', 'POST'])
def GetInfoPath():
        data,info_data = get_request_info_data(request)
        result = get_info_path(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnails_directory', methods=['GET', 'POST'])
def GetThumbnailsDirectory():
        data,info_data = get_request_info_data(request)
        result = get_thumbnails_directory(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_data', methods=['GET', 'POST'])
def GetThumbnailData():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_data(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_rndm_thumbnail', methods=['GET', 'POST'])
def GetRndmThumbnail():
        data,info_data = get_request_info_data(request)
        result = get_rndm_thumbnail(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_items', methods=['GET', 'POST'])
def GetThumbnailItems():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_items(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_frame', methods=['GET', 'POST'])
def GetThumbnailFrame():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_frame(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/is_within_frames', methods=['GET', 'POST'])
def IsWithinFrames():
        data,info_data = get_request_info_data(request)
        result = is_within_frames(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/assure_valid_thumbnail', methods=['GET', 'POST'])
def AssureValidThumbnail():
        data,info_data = get_request_info_data(request)
        result = assure_valid_thumbnail(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_path', methods=['GET', 'POST'])
def GetThumbnailPath():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_path(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_alt', methods=['GET', 'POST'])
def GetThumbnailAlt():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_alt(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_metadata', methods=['GET', 'POST'])
def GetThumbnailMetadata():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_metadata(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_seo_data', methods=['GET', 'POST'])
def GetThumbnailSeoData():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_seo_data(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_id', methods=['GET', 'POST'])
def GetVideoId():
        data,info_data = get_request_info_data(request)
        result = get_video_id(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_link', methods=['GET', 'POST'])
def GetThumbnailLink():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_link(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_audio_path', methods=['GET', 'POST'])
def GetAudioPath():
        data,info_data = get_request_info_data(request)
        result = get_audio_path(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_audio_link', methods=['GET', 'POST'])
def GetAudioLink():
        data,info_data = get_request_info_data(request)
        result = get_audio_link(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_path', methods=['GET', 'POST'])
def GetVideoPath():
        data,info_data = get_request_info_data(request)
        result = get_video_path(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_link', methods=['GET', 'POST'])
def GetVideoLink():
        data,info_data = get_request_info_data(request)
        result = get_video_link(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_keywords', methods=['GET', 'POST'])
def GetKeywords():
        data,info_data = get_request_info_data(request)
        result = get_keywords(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_keywords_str', methods=['GET', 'POST'])
def GetKeywordsStr():
        data,info_data = get_request_info_data(request)
        result = get_keywords_str(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_description', methods=['GET', 'POST'])
def GetVideoDescription():
        data,info_data = get_request_info_data(request)
        result = get_video_description(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_title', methods=['GET', 'POST'])
def GetVideoTitle():
        data,info_data = get_request_info_data(request)
        result = get_video_title(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_whisper_result', methods=['GET', 'POST'])
def GetWhisperResult():
        data,info_data = get_request_info_data(request)
        result = get_whisper_result(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_whisper_text', methods=['GET', 'POST'])
def GetWhisperText():
        data,info_data = get_request_info_data(request)
        result = get_whisper_text(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_whisper_segments', methods=['GET', 'POST'])
def GetWhisperSegments():
        data,info_data = get_request_info_data(request)
        result = get_whisper_segments(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_embed', methods=['GET', 'POST'])
def GetVideoEmbed():
        data,info_data = get_request_info_data(request)
        result = get_video_embed(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_publication_date', methods=['GET', 'POST'])
def GetPublicationDate():
        data,info_data = get_request_info_data(request)
        result = get_publication_date(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_social_metadata', methods=['GET', 'POST'])
def GetVideoSocialMetadata():
        data,info_data = get_request_info_data(request)
        result = get_video_social_metadata(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_schema_markup', methods=['GET', 'POST'])
def GetVideoSchemaMarkup():
        data,info_data = get_request_info_data(request)
        result = get_video_schema_markup(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_captions_path', methods=['GET', 'POST'])
def GetVideoCaptionsPath():
        data,info_data = get_request_info_data(request)
        result = get_video_captions_path(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_captions_link', methods=['GET', 'POST'])
def GetVideoCaptionsLink():
        data,info_data = get_request_info_data(request)
        result = get_video_captions_link(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_captions_data', methods=['GET', 'POST'])
def GetVideoCaptionsData():
        data,info_data = get_request_info_data(request)
        result = get_video_captions_data(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_duration', methods=['GET', 'POST'])
def GetVideoDuration():
        data,info_data = get_request_info_data(request)
        result = get_video_duration(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_file_metadata', methods=['GET', 'POST'])
def GetVideoFileMetadata():
        data,info_data = get_request_info_data(request)
        result = get_video_file_metadata(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_info_data', methods=['GET', 'POST'])
def GetVideoInfoData():
        data,info_data = get_request_info_data(request)
        result = get_video_info_data(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_thumbnail_info', methods=['GET', 'POST'])
def GetThumbnailInfo():
        data,info_data = get_request_info_data(request)
        result = get_thumbnail_info(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/create_video_schema_markeup', methods=['GET', 'POST'])
def CreateVideoSchemaMarkeup():
        data,info_data = get_request_info_data(request)
        result = create_video_schema_markeup(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/create_video_social_metadata', methods=['GET', 'POST'])
def CreateVideoSocialMetadata():
        data,info_data = get_request_info_data(request)
        result = create_video_social_metadata(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/create_video_meta_data', methods=['GET', 'POST'])
def CreateVideoMetaData():
        data,info_data = get_request_info_data(request)
        result = create_video_meta_data(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_video_data', methods=['GET', 'POST'])
def GetVideoData():
        data,info_data = get_request_info_data(request)
        result = get_video_data(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
@call_routes_bp.route('/get_intial_video_data', methods=['GET', 'POST'])
def GetIntialVideoData():
        data,info_data = get_request_info_data(request)
        result = get_intial_video_data(video_id=info_data.get('video_id'),
             info_data=info_data)
        return jsonify({"result":result}), 200
        
