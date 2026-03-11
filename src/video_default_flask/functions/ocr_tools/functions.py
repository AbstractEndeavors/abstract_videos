import spacy,pytesseract,cv2
from PIL import Image
import numpy as np
import PyPDF2
import argparse
from pdf2image import convert_from_path

from abstract_math import (divide_it,
                           multiply_it)

from abstract_utilities import (timestamp_to_milliseconds,
                                format_timestamp,
                                get_time_now_iso,
                                parse_timestamp,
                                get_logFile,
                                url_join,
                                make_dirs,
                                safe_dump_to_file,
                                safe_read_from_json,
                                read_from_file,
                                write_to_file,
                                os,
                                sys,
                                json,
                                glob,
                                datetime,
                                timedelta,
                                logging,
                                shutil,
                                re,
                                path_join,
                                confirm_type,
                                get_media_types,
                                get_all_file_types,
                                eatInner,
                                eatOuter,
                                eatAll)
                                
from abstract_ocr.functions import *                                
logger = get_logFile('vid_to_aud')
logger.debug(f"Logger initialized with {len(logger.handlers)} handlers: {[h.__class__.__name__ for h in logger.handlers]}")

def create_key_value(json_obj, key, value):
    json_obj[key] = json_obj.get(key, value) or value
    return json_obj

def getPercent(i):
    return divide_it(i, 100)

def getPercentage(num, i):
    percent = getPercent(i)
    percentage = multiply_it(num, percent)
    return percentage

def if_none_get_def(value, default):
    if value is None:
        value = default
    return value

def if_not_dir_return_None(directory):
    str_directory = str(directory)
    if os.path.isdir(str_directory):
        return str_directory
    return None

def determine_remove_text(text,remove_phrases=None):
    remove_phrases=remove_phrases or []
    found = False
    for remove_phrase in remove_phrases:
        if remove_phrase in text:
            found = True
            break
    if found == False:
        return text


