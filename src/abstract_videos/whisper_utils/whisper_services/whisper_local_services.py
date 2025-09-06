from .routes import *
def transcribe_with_whisper_local(
    audio_path: str,
    model_size: str = "tiny",           # one of "tiny", "base", "small", "medium", "large"
    language: str = "english",
    use_silence=True,
    info_data=None):
    info_data =info_data or {}
    audio_path = audio_path or os.getcwd()
    if audio_path and os.path.isdir(audio_path):
        audio_path = os.path.join(audio_path,'audio.wav')
    info_data =info_data or {}
    # parameters for fixed chunki)
    """
    Returns the full transcript as a string.
    """
    model = whisper.load_model(model_size)           # loads to GPU if available
    # options: you can pass `task="translate"` for translating to English
 
    result = model.transcribe(audio_path, language=language)
    return result
