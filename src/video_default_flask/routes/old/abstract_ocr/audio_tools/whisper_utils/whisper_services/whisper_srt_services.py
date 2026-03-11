from .routes import *
def export_srt_whisper(whisper_json: dict, output_path: str):
    """
    Write an .srt file from Whisper's verbose_json format.
    `whisper_json["segments"]` should be a list of {start,end,text,...}.
    """
    logger.info(f"export_srt_whisper: {output_path}")
    segments = whisper_json.get("segments", [])
    output_path= output_path or os.getcwd()
    if output_path and os.path.isdir(output_path):
        output_path = os.path.join(output_path,'captions.srt')
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, start=1):
            start_ts = _format_srt_timestamp(seg["start"])
            end_ts   = _format_srt_timestamp(seg["end"])
            text     = seg["text"].strip()
            f.write(f"{idx}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{text}\n\n")
            
def export_srt(audio_text, output_path):
    logger.info(f"export_srt: {output_path}")
    with open(output_path, 'w') as f:
        for i, entry in enumerate(audio_text, 1):
            start = entry['start_time'].replace('.', ',')
            end = entry['end_time'].replace('.', ',')
            f.write(f"{i}\n{start} --> {end}\n{entry['text']}\n\n")
    result = model.transcribe(audio_path, language=language)
    info_data["whisper_result"] = result
    return info_data
