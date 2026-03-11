from .route_vars import *
from ..functions.service_calls.text_tools.keybert_utils import KeywordManager
from ..functions.service_calls.text_tools.summarizer_utils import SummarizerManager
from ..functions.service_calls.audio_tools.whisper_utils import WhisperManager
from ..functions.service_calls.video_tools import VideoTextManager
from ..functions.service_calls.info_utils.initial_info import get_initial_info_data
from ..functions.service_calls.seo_utils.seo_manager import SEOManager
from abstract_utilities import get_all_file_types,os
import hashlib
from flask import Flask, request, jsonify
from transformers import pipeline
from keybert import KeyBERT
import whisper
import os
import tempfile
import logging
from ..functions.service_calls.ocr_utils import get_video_info_data,get_video_info_data,get_video_info_path,get_videos_path
from abstract_videos import *
import os
from pathlib import Path
from typing import List, Dict, Any
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import json
# Paths

filepath = os.path.abspath(__file__)
service_calls_bp,logger = get_bp(filepath)
seo_mgr = SEOManager()
video_text_mgr = VideoTextManager()
kw_mgr = KeywordManager()
summ_mgr = SummarizerManager()
whisper_mgr = WhisperManager()
app = Flask(__name__)



TEXT_DIR = "/var/www/typicallyoutliers/frontend/public/repository/text_dir"
VIDEOS_DIR = "/var/www/typicallyoutliers/frontend/public/repository/videos"
TEXT_DIR = "/var/www/typicallyoutliers/frontend/public/repository/text_dir"
VIDEOS_DIR = "/var/www/typicallyoutliers/frontend/public/repository/videos"
# Define TEXT_DIR
TEXT_DIR = "/var/www/typicallyoutliers/frontend/public/repository/text_dir"

def get_all_available_videos(text_dir: str = TEXT_DIR) -> List[str]:
    """
    List all subdirectories in text_dir containing info.json.
    """
    return [p.name for p in Path(text_dir).iterdir() if p.is_dir() and (p / "info.json").is_file()]

def convert_to_server_doc(path: str) -> str:
    """
    Convert paths from computron mount to server path.
    """
    if isinstance(path, str):
        return path.replace('/home/computron/mnt/webserver/typicallyoutliers/', '/var/www/typicallyoutliers/')
    return path

def convert_to_link(path: str) -> str:
    """
    Convert local paths to public URLs, accounting for assetPrefix: '/app'.
    """
    if isinstance(path, str):
        return path.replace('/var/www/typicallyoutliers/frontend/public', 'https://typicallyoutliers.com')
    return path

def if_og_change(path: str, og_path: str, new_path: str) -> str:
    """
    Replace original path with new path if they match.
    """
    if isinstance(path, str) and path == og_path:
        return new_path
    return path

def change_all_link_paths(path: Any, og_path: str, new_path: str) -> Any:
    """
    Apply path replacement and convert to public URL.
    """
    if isinstance(path, str):
        path = if_og_change(path, og_path, new_path)
        path = convert_to_link(path)
    return path

def get_key_values(dict_obj: Any) -> Dict[str, Any]:
    """
    Update all relevant paths in the video metadata dictionary to public URLs.
    """
    try:
        # Handle string input (file path or JSON string)
        if isinstance(dict_obj, str):
            dict_obj = convert_to_server_doc(dict_obj)
            try:
                # Try parsing as JSON string
                dict_obj = json.loads(dict_obj)
            except json.JSONDecodeError:
                # Assume it's a file path
                if not os.path.exists(dict_obj):
                    raise FileNotFoundError(f"JSON file not found: {dict_obj}")
                with open(dict_obj, 'r') as f:
                    dict_obj = json.load(f)

        # Validate that dict_obj is a dictionary
        if not isinstance(dict_obj, dict):
            raise ValueError(f"Expected a dictionary, got {type(dict_obj)}: {dict_obj}")

        # Extract key fields
        og_video_path = dict_obj.get("video_path", "")
        video_dir = dict_obj.get("info_dir", "")
        filename = dict_obj.get("video_id", "")
        ext = dict_obj.get("video_metadata", {}).get("format", "mp4").lower()
        
        # Handle .flv vs .mp4 mismatch
        if ext == "flv" and os.path.exists(os.path.join(video_dir, f"{filename}.mp4")):
            ext = "mp4"
        
        basename = f"{filename}.{ext}"
        video_path = os.path.join(video_dir, basename)
        video_link = change_all_link_paths(video_path, og_video_path, video_path)
        
        # Update video_path and other known path fields
        dict_obj["video_path"] = video_link
        if "captions_path" in dict_obj:
            dict_obj["captions_path"] = change_all_link_paths(dict_obj["captions_path"], og_video_path, video_path)
        if "thumbnail" in dict_obj and isinstance(dict_obj["thumbnail"], dict):
            dict_obj["thumbnail"]["file_path"] = change_all_link_paths(
                dict_obj["thumbnail"].get("file_path", ""), og_video_path, video_path
            )
        if "schema_markup" in dict_obj and isinstance(dict_obj["schema_markup"], dict):
            for field in ["thumbnailUrl", "contentUrl"]:
                if field in dict_obj["schema_markup"]:
                    dict_obj["schema_markup"][field] = change_all_link_paths(
                        dict_obj["schema_markup"][field], og_video_path, video_path
                    )
        if "social_metadata" in dict_obj and isinstance(dict_obj["social_metadata"], dict):
            for field in ["og:image", "og:video", "twitter:image"]:
                if field in dict_obj["social_metadata"]:
                    dict_obj["social_metadata"][field] = change_all_link_paths(
                        dict_obj["social_metadata"][field], og_video_path, video_path
                    )

        # Process all fields recursively
        for key, value in dict_obj.items():
            if isinstance(value, str):
                dict_obj[key] = change_all_link_paths(value, og_video_path, video_path)
            elif isinstance(value, list):
                dict_obj[key] = [
                    change_all_link_paths(item, og_video_path, video_path) if isinstance(item, str) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                dict_obj[key] = {
                    k: change_all_link_paths(v, og_video_path, video_path) if isinstance(v, str) else v
                    for k, v in value.items()
                }
        
        # Map to VideoData interface
        dict_obj["video_url"] = dict_obj["video_path"]
        dict_obj["thumbnail_url"] = dict_obj.get("thumbnail", {}).get("file_path", "")
        dict_obj["id"] = dict_obj.get("video_id", "")
        dict_obj["social_meta"] = dict_obj.get("social_metadata", {})
        return dict_obj
    except Exception as e:
        print(f"Error processing dictionary: {e}")
        return {}
def get_all_avalable_video_info():
    all_vaid_infos = []
    for video_path in get_all_file_types('video',TEXT_DIR):
        video_dir = os.path.dirname(video_path)
        info_path = os.path.join(video_dir,"info.json")
        info_data = safe_read_from_json(info_path)
        
        processed_steps = info_data.get("processed_steps") or {}
        if processed_steps and processed_steps.get("conversion") == True:
            all_vaid_infos.append(info_data)
    return all_vaid_infos
def generate_description_and_keywords(transcription):
        """Generate description and keywords using Transformers and KeyBERT."""
   
        # Initialize summarization pipeline
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # Generate description (limit input to avoid excessive length)
        description = summarizer(transcription[:1000], max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        
        # Initialize KeyBERT for keyword extraction
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(
            transcription,
            keyphrase_ngram_range=(1, 2),  # Allow single words and bigrams
            stop_words='english',
            top_n=10
        )
        keywords = [kw[0] for kw in keywords]  # Extract just the keywords

        logger.info("Description and keywords generated successfully")
        return description, keywords
@service_calls_bp.route('/video_text_pipeline', methods=['POST'])
def videoVexPipeline():
    logger.info("Description and keywords generated successfully")
    data,info_data = get_request_info_data(request)
    try:
        video_path =data.get('video_path')
        if video_path:
            new_filename = generate_file_id(video_path)
            ext = extract_ext(video_path)
            output_dir = f"{TEXT_DIR}/{new_filename}"
            filename = f"{new_filename}{ext}"
            output_path = os.path.join(output_dir, new_filename)
            # Initialize pipeline
            pipeline = VideoTextPipeline(
                video_path=video_path,
                output_dir=output_dir,
                output_option="copy",
                output_path=output_path,
                frame_interval=1,
                reencode=True  # Force reencode for .flv
            )
            texts = pipeline.run()
        return jsonify({"result":texts})
    except Exception as e:
        return jsonify({"error":f"{e}"})
@service_calls_bp.route('/generate', methods=['POST'])
def generate():
        """API endpoint to generate description and keywords from transcription."""
   
        data = request.get_json()
        if not data or 'transcription' not in data:
            return jsonify({"error": "Missing 'transcription' in request body"}), 400

        transcription = data['transcription']
        if not isinstance(transcription, str) or not transcription.strip():
            return jsonify({"error": "Invalid or empty transcription"}), 400

        description, keywords = generate_description_and_keywords(transcription)
        if description is None or keywords is None:
            return jsonify({"error": "Failed to generate description/keywords"}), 500

        return jsonify({
            "description": description,
            "keywords": keywords
        }), 200

 

def transcribe_audio(audio_path, model_size="tiny", language="english"):
        """Transcribe audio to text using Whisper."""
    
        logger.info(f"Transcribing audio: {audio_path}")
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path, language=language)
        transcription = result["text"]
        logger.info("Transcription completed successfully")
        return transcription


def generate_description_and_keywords(transcription):
        """Generate description and keywords using Transformers and KeyBERT."""
   
        # Initialize summarization pipeline
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # Generate description (limit input to avoid excessive length)
        description = summarizer(transcription[:1000], max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        
        # Initialize KeyBERT for keyword extraction
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(
            transcription,
            keyphrase_ngram_range=(1, 2),  # Allow single words and bigrams
            stop_words='english',
            top_n=10
        )
        keywords = [kw[0] for kw in keywords]  # Extract just the keywords

        logger.info("Description and keywords generated successfully")
        return description, keywords

@app.route('/transcribe', methods=['POST'])
def transcribe():
        """API endpoint to transcribe an audio file."""
   
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Save the audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name

        # Transcribe the audio
        transcription = transcribe_audio(temp_audio_path)
        
        # Clean up the temporary file
        os.unlink(temp_audio_path)

        if transcription is None:
            return jsonify({"error": "Failed to transcribe audio"}), 500

        return jsonify({"transcription": transcription}), 200


@app.route('/generate', methods=['POST'])
def generate():
        """API endpoint to generate description and keywords from transcription."""
  
        data = request.get_json()
        if not data or 'transcription' not in data:
            return jsonify({"error": "Missing 'transcription' in request body"}), 400

        transcription = data['transcription']
        if not isinstance(transcription, str) or not transcription.strip():
            return jsonify({"error": "Invalid or empty transcription"}), 400

        description, keywords = generate_description_and_keywords(transcription)
        if description is None or keywords is None:
            return jsonify({"error": "Failed to generate description/keywords"}), 500

        return jsonify({
            "description": description,
            "keywords": keywords
        }), 200

@service_calls_bp.route("/get_initial_info_data", methods=["POST"])
def getInitialInfoData():
    logger.info("Description and keywords generated successfully")
    req = request
    data,info_data = get_request_info_data(request)
    updated = get_initial_info_data(req=request, info_data=info_data)
    return jsonify(updated)

@service_calls_bp.route("/extract_video_text", methods=["POST"])
def extract_video_text():
    
    data,info_data = get_request_info_data(request)
    updated = video_text_mgr.run(req=request, info_data=info_data)
    return jsonify(updated)

@service_calls_bp.route("/transcribe", methods=["POST"])
def transcribe():
    data,info_data = get_request_info_data(request)
    updated = whisper_mgr.run(req=request, info_data=info_data)
    return jsonify(updated)
@service_calls_bp.route("/get_whisper_result_data", methods=["POST"])
def getWhisperResultData():
    data,info_data = get_request_info_data(request)
    updated = get_whisper_result_data(req=request, info_data=info_data)
    return jsonify(updated)
@service_calls_bp.route("/get_whisper_text", methods=["POST"])
def getWhispeText():
    data,info_data = get_request_info_data(request)
    updated = get_whisper_text(req=request, info_data=info_data)
    return jsonify(updated)
from flask import request, jsonify

@service_calls_bp.route("/get_whisper_segment", methods=["POST"])
def get_whisper_segment():
    data,info_data = get_request_info_data(request)   # <-- no more Request object
    logger.info(f"info_data == {info_data}")
    logger.info(f"data == {data}")
    updated = whisper_mgr.run(req=request, info_data=info_data)
    logger.info(f"updated == {updated}")
    return jsonify(updated)
@service_calls_bp.route("/generate_keywords", methods=["POST"])
def generate_keywords():
    data,info_data = get_request_info_data(request)
    new_info = kw_mgr.run(req=request, info_data=info_data)
    return jsonify(new_info)



@service_calls_bp.route("/generate_seo", methods=["POST"])
def generate_seo():
    data,info_data = get_request_info_data(request)
    updated = seo_mgr.run(req=request, info_data=info_data)
    return jsonify(updated)

@service_calls_bp.route('/get_available_raw_video_list', methods=['GET', 'POST'])
def getAvailableRawVideos():
    available_list = get_all_file_types('video',VIDEOS_DIR)
    return jsonify({"result":available_list})

@service_calls_bp.route('/get_available_video_info', methods=['GET', 'POST'])
def getDAvailableVideoInfo():
    available_list = get_all_avalable_video_info()
    available_list = [get_key_values(available_item) for available_item in available_list]
    return jsonify({"result":available_list})


@service_calls_bp.route('/get_video_info_dir', methods=['GET', 'POST'])
def getVideoInfoDir():
    data,info_data = get_request_info_data(request)
    logger.info(f"data == {data}")
    result = get_video_info_dir(**data)
    logger.info("Description and keywords generated successfully")
    return jsonify({"result":result})
