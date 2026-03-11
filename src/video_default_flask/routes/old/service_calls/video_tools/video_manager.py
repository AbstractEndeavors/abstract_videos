# Actually, only a few imports are needed. Let’s clean up:
from .video_call_schema import get_video_text_input_keys, get_video_text_bool_key
from .routes import get_key_vars, get_bool_response, get_video_info_path
from .video_pipeline import VideoTextPipeline

class VideoTextManager:
    """
    Orchestrates the video-text (OCR) pipeline step:
      1) fetch inputs (video_path, thumbnails_directory, remove_phrases, video_id)
      2) check if OCR is needed
      3) run the VideoTextPipeline
      4) persist updated info_data
    """
    def fetch_vars(self, req=None, info_data=None):
        # get the minimal set of variables needed
        keys = get_video_text_input_keys()
        new_data, info_data = get_key_vars(keys, req=req, info_data=info_data)
        return new_data, info_data

    def should_run(self, req=None, info_data=None):
        # use the schema's boolean key helper
        run_flag, info_data = get_video_text_bool_key(req=req, info_data=info_data)
        return run_flag, info_data

    def run(self, req=None, info_data=None):
        # 1) fetch variables
        new_data, info_data = self.fetch_vars(req=req, info_data=info_data)
        # 2) decide whether to run OCR
        run_flag, info_data = self.should_run(req=req, info_data=info_data)
        if not run_flag:
            return info_data

        # 3) run the pipeline
        pipeline = VideoTextPipeline(req=req, info_data=info_data)
        texts = pipeline.run()

        # pipeline.run() writes directly into pipeline.info
        updated_info = pipeline.info

        # 4) persist the updated info_data
        out_path = get_video_info_path(**updated_info)
        safe_dump_to_file(data=updated_info, file_path=out_path)

        return updated_info
