from ..routes import *
from transformers import pipeline
import torch,os,json,unicodedata,hashlib
from ..whisper_utils import *
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
    get_result_from_data,
    remove_path,
    remove_directory,
    make_list_it
    )
import spacy

##from .keybert_utils.keybert_manager import KeywordManager
#from .summarizer_utils.summarizer_manager import SummarizerManager

