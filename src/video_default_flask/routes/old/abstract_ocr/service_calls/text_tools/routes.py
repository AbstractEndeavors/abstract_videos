from ..routes import *
from transformers import pipeline
import torch,os,json,unicodedata,hashlib
from ..audio_tools import *
from abstract_utilities import (
    Counter,
    get_logFile,
    List,
    shutil,
    Optional,
    safe_save_updated_json_data,
    get_result_from_data,
    remove_path,
    remove_directory,
    make_list_it,
    List,
    shutil,
    Optional,
    get_bool_response,
    safe_save_updated_json_data,
    safe_read_from_json,
    get_result_from_data,
    remove_path,
    remove_directory,
    make_list_it
    )
import spacy

from .keybert_utils.keybert_manager import KeywordManager
from .summarizer_utils.summarizer_manager import SummarizerManager
kw_mgr = KeywordManager()
summ_mgr = SummarizerManager()

@app.route("/generate_keywords", methods=["POST"])
def generate_keywords():
    req = request
    info = load_existing_info_for(req)
    new_info = kw_mgr.run(req=req, info_data=info)
    return jsonify(new_info)



@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    req = request
    info = load_existing_info_for(req)
    updated = summ_mgr.run(req=req, info_data=info)
    return jsonify(updated)
