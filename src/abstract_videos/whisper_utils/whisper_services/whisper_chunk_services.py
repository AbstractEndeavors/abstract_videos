from .routes import *
import numpy as np
from typing import *
from pydub import AudioSegment
from pydub.silence import split_on_silence
def chunk_fixed(
    audio_array: np.ndarray,
    sr: int = 16000,
    chunk_length_s: int = 30,
    overlap_s: int = 5
) -> List[np.ndarray]:
    """
    Split a numpy audio array into fixed-size chunks with overlap.
    """
    chunk_len = chunk_length_s * sr
    overlap  = overlap_s  * sr
    step     = chunk_len - overlap
    total    = audio_array.shape[0]
    chunks: List[np.ndarray] = []
    for start in range(0, total, step):
        end = min(start + chunk_len, total)
        chunks.append(audio_array[start:end])
        if end == total:
            break
    return chunks

def chunk_on_silence(
    audio_path: str,
    min_silence_len: int = 700,
    silence_thresh: Optional[int] = None,
    keep_silence: int = 300
) -> List[AudioSegment]:
    """
    Load the file and split on silent parts.
    Returns a list of pydub AudioSegment chunks.
    """
    audio = AudioSegment.from_file(audio_path)
    # dynamically set threshold ~16 dB below average loudness
    silence_thresh = silence_thresh or int(audio.dBFS) - 16
    return split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence
    )
def transcribe_in_chunks(
    audio_path: str,
    model_size: str      = "medium",
    language: Optional[str] = None,
    use_silence: bool    = True,
    info_data = None,
    # parameters for fixed chunking:
    chunk_length_s: int  = 30,
    overlap_s: int       = 5,
    # parameters for silence chunking:
    min_silence_len: int = 700,
    keep_silence: int    = 300
) -> str:
    """
    Transcribe by splitting the audio into chunks and stitching results.
    """
    info_data =info_data or {}
    model = whisper.load_model(model_size)
    audio_dir =  make_audio_dir(info_data)
    
    full_text = []
    if use_silence:
        segments = chunk_on_silence(
            audio_path,
            min_silence_len=min_silence_len,
            keep_silence=keep_silence
        )
        audio_paths  = []
        for i, seg in enumerate(segments):
            audio_path = os.path.join(audio_dir,f"chunk_{i}.wav")
            audio_paths.append(audio_path)
            seg.export(audio_path, format="wav")
            res = model.transcribe(audio_path, language=language)
            full_text.append(res["text"].strip())
            remove_path(path=audio_path)
        remove_directory(audio_dir,paths=audio_paths)
    else:
        audio = whisper.load_audio(audio_path)  # returns np.ndarray
        # no need to pad/trim if chunking manually
        chunks = chunk_fixed(
            audio, SAMPLE_RATE,
            chunk_length_s=chunk_length_s,
            overlap_s=overlap_s
        )
        full_text = collate_trans_chunks(chunks=chunks,
                                                 transcribe_func = model.transcribe,
                                                 key="text",
                                                 full_text=full_text,
                                                 language=language)
    result = {"text":" ".join(full_text).strip()}
    info_data["whisper_result"] = result
    return info_data
