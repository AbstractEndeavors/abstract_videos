from .functions import (os,
                        logger,
 
                        AudioSegment,
                        sr,
                        detect_nonsilent,
                        format_timestamp,
                        safe_dump_to_file,
                        )


def get_audio_duration(file_path):
    audio = AudioSegment.from_wav(file_path)
    duration_seconds = len(audio) / 1000
    duration_formatted = format_timestamp(len(audio))
    return duration_seconds,duration_formatted
def transcribe_audio_file_clean(
    audio_path: str,
    json_data: str = None,
    min_silence_len: int = 500,
    silence_thresh_delta: int = 16
    ):
    """
    Load `audio_path`, detect all non-silent ranges, transcribe each,
    and (optionally) dump to JSON at `output_json`.
    """
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(audio_path)

    # 1) Calibrate once on the first second
    calib = audio[:1000]
    calib_path = os.path.join(os.path.dirname(audio_path), "_calib.wav")
    calib.export(calib_path, format="wav")
    with sr.AudioFile(calib_path) as src:
        recognizer.adjust_for_ambient_noise(src, duration=1)
    os.remove(calib_path)

    # 2) Compute dynamic silence threshold, then find real speech segments
    silence_thresh = audio.dBFS - silence_thresh_delta
    nonsilent = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    
    json_data["audio_text"] = []
    for idx, (start_ms, end_ms) in enumerate(nonsilent):
        logger.info(f"Transcribing segment {idx}: {start_ms}-{end_ms} ms")
        chunk = audio[start_ms:end_ms]

        chunk_path = f"_chunk_{idx}.wav"
        chunk.export(chunk_path, format="wav")

        with sr.AudioFile(chunk_path) as src:
            audio_data = recognizer.record(src)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = ""

        json_data["audio_text"].append({
            "start_time": format_timestamp(start_ms),
            "end_time": format_timestamp(end_ms),
            "text": text
        })
        os.remove(chunk_path)

    # 3) Optionally write out the JSON

        full_text = [ entry["text"] 
                for entry in json_data.get("audio_text", []) 
                if entry.get("text") ]
        full_text = " ".join(full_text).strip()
        json_data["full_text"] = full_text
        safe_dump_to_file(json_data, json_data['info_path'])
    
    return json_data


