from abstract_ocr import *
from ..modules import *
from ...routes.route_vars import *
REMOVE_PHRASES = ['Video Converter', 'eeso', 'Auseesott', 'Aeseesott', 'esoft']
def create_video_info(video_path,
                      output_dir=None,
                      remove_phrases=None,
                      summarizer=None,
                      kw_model=None,
                      uploader=None,
                      domain=None,
                      categories=None,
                      videos_url=None,
                      chunk_length_ms=None,
                      chunk_length_diff=None,
                      renew=None,
                      *args,
                      **kwargs):
    output_dir = output_dir or VIDEO_OUTPUT_DIR
    remove_phrases = remove_phrases or REMOVE_PHRASES
    info = transcribe_video_path(video_path=video_path,
                              output_dir=output_dir,
                              remove_phrases=remove_phrases,
                              summarizer=summarizer,
                              kw_model=kw_model,
                              uploader=uploader,
                              domain=domain,
                              categories=categories,
                              videos_url=VIDEOS_URL,
                              chunk_length_ms=chunk_length_ms,
                              chunk_length_diff=chunk_length_diff,
                              renew=renew)
    return info

def create_all_video_info(video_path,
                      output_dir=None,
                      remove_phrases=None,
                      summarizer=None,
                      kw_model=None,
                      uploader=None,
                      domain=None,
                      categories=None,
                      videos_url=None,
                      chunk_length_ms=None,
                      chunk_length_diff=None,
                      renew=None,
                      *args,
                      **kwargs):
    output_dir = output_dir or VIDEO_OUTPUT_DIR
    remove_phrases = remove_phrases or REMOVE_PHRASES
    transcribe_all_video_paths(directory=VIDEOS_DIR,
                               output_dir=output_dir,
                              remove_phrases=remove_phrases,
                              summarizer=summarizer,
                              kw_model=kw_model,
                              uploader=uploader,
                              domain=domain,
                              categories=categories,
                              videos_url=VIDEOS_URL,
                              chunk_length_ms=chunk_length_ms,
                              chunk_length_diff=chunk_length_diff,
                              renew=renew)
    return True

