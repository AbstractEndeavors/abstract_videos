from .route_vars import *
from .text_tools.keybert_utils import KeywordManager
from .text_tools.summarizer_utils import SummarizerManager
from .audio_tools.whisper_utils import WhisperManager
from .video_tools import VideoTextManager
from .info_utils.initial_info import get_initial_info_data
from .seo_utils.seo_manager import SEOManager
from abstract_utilities import get_all_file_types
import hashlib
from flask import Flask, request, jsonify
from transformers import pipeline
from keybert import KeyBERT
import whisper
import os
import tempfile
import logging
from .ocr_utils import get_video_info_data,get_video_info_data,get_video_info_path,get_videos_path
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
def get_all_available_videos(text_dir: str = TEXT_DIR) -> List[str]:
    """
    List all subdirectories in text_dir containing info.json.
    """
    return [p.name for p in Path(text_dir).iterdir() if p.is_dir() and (p / "info.json").is_file()]
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
    logger.info("get_whisper_segment")
    payload = request.get_json(force=True)              # <-- dict now
    logger.info("payload == {payload}")
    data, info_data = get_request_info_data(payload)    # <-- no more Request object
    logger.info("info_data == {info_data}")
    logger.info("data == {data}")
    updated = whisper_mgr.run(req=payload, info_data=info_data)
    logger.info("updated == {updated}")
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




