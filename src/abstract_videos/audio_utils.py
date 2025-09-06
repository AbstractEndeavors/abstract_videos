import moviepy.editor as mp
from moviepy.editor import *
from.file_utils import logger
import whisper
def extract_audio_from_video(video_path, audio_path=None):
    """Extract audio from a video file using moviepy."""
    if audio_path == None:
        video_directory = os.path.dirname(video_path)
        audio_path = video_directory
    if os.path.isdir(audio_path):
        audio_path = os.path.join(audio_path,'audio.wav')
    try:
        logger.info(f"Extracting audio from {video_path} to {audio_path}")
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        video.close()
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file {audio_path} was not created.")
        logger.info(f"Audio extracted successfully: {audio_path}")
        return audio_path
    except Exception as e:
        logger.error(f"Error extracting audio from {video_path}: {e}")
        return None
def transcribe_with_whisper_local(
    audio_path: str,
    model_size: str = "tiny",           # one of "tiny", "base", "small", "medium", "large"
    language: str = "english",
    use_silence=True):
    # parameters for fixed chunki)
    """
    Returns the full transcript as a string.
    """
    model = whisper.load_model(model_size)           # loads to GPU if available
    # options: you can pass `task="translate"` for translating to English
 
    result = model.transcribe(audio_path, language=language)
    return result
