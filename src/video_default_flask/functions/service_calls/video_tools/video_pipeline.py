import os
from abstract_ocr.ocr_utils import extract_image_texts_from_directory
from moviepy.editor import VideoFileClip
from abstract_utilities.json_utils import safe_update_json_datas


from .routes import *
from .routes import *
def is_video_text_data(**info_data):
    bool_key = info_data.get('video_text') == None
    return bool_key

def get_video_text_input_keys():
     keys = ['video_path',
            'thumbnails_directory',
            'remove_phrases',
            'video_id']
     return keys
def get_video_text_key_vars(req=None,info_data=None):
    keys = get_video_text_input_keys()
    new_data,info_data = get_key_vars(keys=keys,
                                      req=req,
                                      info_data=info_data
                                      )
    return new_data,info_data
def get_video_text_bool_key(req=None,info_data=None):
    new_data,info_data = get_video_text_key_vars(req=req,
                                              info_data=info_data)
    bool_response = is_video_text_data(**info_data)
    return get_bool_response(bool_response,info_data),info_data
def transcribe_with_video_text_call(req=None,info_data=None):
    bool_key,info_data = get_video_text_bool_key(req=req,
                                    info_data=info_data)
    function = get_analyze_video_text_data
    return function,bool_key
def get_video_text_execution_variables(req=None,info_data=None):
    keys = get_video_text_input_keys()
    function,bool_key = transcribe_with_video_text_call(req=req,
                                                     info_data=info_data)
    return keys,function,bool_key


class VideoTextPipeline:
    def __init__(self, new_data=None,info_data=None):
        """
        info_data must contain at least:
          - video_path
          - thumbnails_directory
          - video_id
          - remove_phrases (optional)
          - frame_interval (optional)
        """
        self.info = info_data
        self.new_data = new_data
    def needs_processing(self) -> bool:
        # mirror your is_video_text_data check
        return self.new_data.get("video_text") is None

    def extract_frames(self):
        video_path = self.new_data["video_path"]
        directory  = self.new_data["thumbnails_directory"]
        interval   = self.new_data.get("frame_interval", 1)
        vid_id     = self.new_data["video_id"]

        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        audio_path = self.info.get("audio_path") or self.info.get("info_dir") or self.info.get("info_directory")
        audio_path = audio_path
        if audio_path and os.path.isdir(audio_path):
            audio_path = os.path.join(audio_path,'audio.wav')
        extract_audio_from_video_call(audio_path=audio_path,video_path=video_path)
        os.makedirs(directory, exist_ok=True)
        for t in range(0, duration, interval):
            frame_file = os.path.join(directory, f"{vid_id}_frame_{t}.jpg")
            if not os.path.isfile(frame_file):
                frame = clip.get_frame(t)
                # cv2 import assumed in your routes.py
                import cv2, numpy as np
                cv2.imwrite(frame_file, cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))

    def ocr_images(self, existing_texts=None):
        return extract_image_texts_from_directory(
            directory=self.new_data["thumbnails_directory"],
            image_texts=existing_texts or [],
            remove_phrases=self.new_data.get("remove_phrases", []),
        )

    def run(self):
        """Perform the full OCR pipeline and update info_data & JSON on disk."""
        if not self.needs_processing():
            return self.new_data["video_text"]

        # 1) extract frames
        self.extract_frames()

        # 2) OCR-the-frames
        texts = self.ocr_images(existing_texts=self.new_data.get("video_text"))
        self.new_data["video_text"] = texts

        # 3) persist to your JSON store
        #    update_json_data comes from abstract_utilities.json_utils
        
        self.info = update_json_data(self.info, self.new_data, keys=True)
        return texts
def execute_video_text_variables(req=None, info_data=None):
     # 1) pull out the whisper inputs (audio_path, model_size, etc.)
    new_data, info_data = get_video_text_key_vars(req=req, info_data=info_data)  # :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}

    # 2) decide if we need to run (same as your bool-utils approach)
    should_run, info_data = get_video_text_bool_key(req=req, info_data=info_data) 
    if should_run:
        # 3) run the pipeline, which returns {'text':…, 'segments':…}
        pipeline = VideoTextPipeline(new_data, info_data)                                # :contentReference[oaicite:4]{index=4}&#8203;:contentReference[oaicite:5]{index=5}
        info = pipeline.run()
        info_data = update_json_data(info_data, info, keys=True)
        # 4) merge the result back into info_data
    info_data = update_json_data(info_data, new_data, keys=True)
    logger.info(f" for execute_video_text_variables ||| THIS IS THE GODDAMN INF FUCKING DATA{info_data}")
    return info_data   

