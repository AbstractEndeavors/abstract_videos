import os
import json
from urllib.parse import quote
from typing import Dict, Optional
import ffmpeg
from datetime import datetime
import datetime

BASE_URL = "https://typicallyoutliers.com"
REPO_DIR = "/var/www/typicallyoutliers/frontend/public/repository/"
INFOS_DIR = '/var/www/typicallyoutliers/frontend/public/repository/text_dir/'
VIDEO_DIR = '/var/www/typicallyoutliers/frontend/public/repository/Video/'
DIR_LINKS = {
    REPO_DIR: 'repository',
    INFOS_DIR: 'infos',
    VIDEO_DIR: 'videos'
}
EXT_TO_PREFIX = {
    **dict.fromkeys(
        {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'},
        'infos'
    ),
    **dict.fromkeys(
        {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'},
        'videos'
    ),
    '.pdf': 'pdfs',
    **dict.fromkeys({'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}, 'audios'),
    **dict.fromkeys({'.doc', '.docx', '.txt', '.rtf'}, 'docs'),
    **dict.fromkeys({'.ppt', '.pptx'}, 'slides'),
    **dict.fromkeys({'.xls', '.xlsx', '.csv'}, 'sheets'),
    **dict.fromkeys({'.srt'}, 'srts')
}
def generate_media_url(fs_path: str) -> str | None:
    fs_path = os.path.abspath(fs_path)
    if not fs_path.startswith(REPO_DIR):
        return None
    rel_path = fs_path[len(REPO_DIR):]
    rel_path = quote(rel_path.replace(os.sep, '/'))
    ext = os.path.splitext(fs_path)[1].lower()
    prefix = EXT_TO_PREFIX.get(ext, 'repository')
    return f"{BASE_URL}/{prefix}/{rel_path}"
def get_link(path: str) -> str | None:
    if path:
        for key, value in DIR_LINKS.items():
            if path.startswith(key):
                if value == 'repository':
                    link = generate_media_url(path)
                else:
                    rel_path = path[len(key):]
                    link = f"{BASE_URL}/{value}/{rel_path}"
                return link
    return None
input(generate_media_url('/var/www/typicallyoutliers/frontend/public/repository/text_dir/(3-of-5)-five-cancer-reversal-testimonies.-b17.-2008./captions.srt'))
EXT_TO_PREFIX = {
    **dict.fromkeys(
        {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'},
        'infos'
    ),
    **dict.fromkeys(
        {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'},
        'videos'
    ),
    '.pdf': 'pdfs',
    **dict.fromkeys({'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}, 'audios'),
    **dict.fromkeys({'.doc', '.docx', '.txt', '.rtf'}, 'docs'),
    **dict.fromkeys({'.ppt', '.pptx'}, 'slides'),
    **dict.fromkeys({'.xls', '.xlsx', '.csv'}, 'sheets'),
    **dict.fromkeys({'.srt'}, 'srts'),
}

def generate_media_url(fs_path: str,repository_dir=None) -> str | None:
    fs_path = os.path.abspath(fs_path)
    if not fs_path.startswith(repository_dir):
        return None
    rel_path = fs_path[len(repository_dir):]
    rel_path = quote(rel_path.replace(os.sep, '/'))
    ext = os.path.splitext(fs_path)[1].lower()
    prefix = EXT_TO_PREFIX.get(ext, 'repository')
    return f"{BASE_URL}/{prefix}/{rel_path}"

def get_link(path: str) -> str | None:
    if path:
        for key, value in DIR_LINKS.items():
            if path.startswith(key):
                if value == 'repository':
                    link = generate_media_url(path)
                else:
                    rel_path = path[len(key):]
                    link = f"{BASE_URL}/{value}/{rel_path}"
                return link
    return None

def generate_with_bigbird(text: str, task: str = "title", model_dir: str = "allenai/led-base-16384") -> str:
    try:
        tokenizer = LEDTokenizer.from_pretrained(model_dir)
        model = LEDForConditionalGeneration.from_pretrained(model_dir)
        prompt = (
            f"Generate a concise, SEO-optimized {task} for the following content: {text[:1000]}"
            if task in ["title", "caption", "description"]
            else f"Summarize the following content into a 100-150 word SEO-optimized abstract: {text[:4000]}"
        )
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(
            inputs["input_ids"],
            max_length=200 if task in ["title", "caption"] else 300,
            num_beams=5,
            early_stopping=True
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Error in BigBird processing: {e}")
        return ""

def extract_video_metadata(video_path: str) -> Dict:
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        if not video_stream:
            print(f"Warning: No video stream found in {video_path}")
            return {}
        metadata = {
            'duration': float(probe['format']['duration']),
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'file_size': f"{int(probe['format']['size']) // 1024}KB",
            'format': probe['format']['format_name'],
            'video_codec': video_stream.get('codec_name', ''),
            'audio_codec': audio_stream.get('codec_name', '') if audio_stream else '',
            'mime_type': 'video/mp4' if video_path.endswith('.mp4') else 'video/webm' if video_path.endswith('.webm') else 'video/unknown'
        }
        return metadata
    except Exception as e:
        print(f"Error extracting video metadata: {e}")
        return {}

def convert_video_to_mp4(input_path: str, output_path: str) -> str:
    try:
        probe = ffmpeg.probe(input_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream and video_stream['codec_name'] == 'h264' and input_path.endswith('.mp4'):
            return input_path
        stream = ffmpeg.input(input_path).output(output_path, vcodec='libx264', acodec='aac', movflags='+faststart')
        ffmpeg.run(stream, overwrite_output=True)
        print(f"Converted {input_path} to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error converting video: {e}")
        return input_path
def generate_video_info_json(video_input: str, output_dir: str, base_url: str = BASE_URL) -> Dict:
  
        # Handle input (URL or path)
        is_url = video_input.startswith(('http://', 'https://'))
        temp_path = None
        if is_url:
            video_url = video_input
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            temp_path = os.path.join('/tmp', os.path.basename(video_url))
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            video_path = temp_path
        else:
            video_path = video_input
            video_url = get_link(video_path) or f"{base_url}/videos/{os.path.basename(video_path)}"

        # Convert to MP4 if necessary
        original_ext = os.path.splitext(video_path)[1].lower()
        if original_ext not in ['.mp4']:
            converted_path = os.path.join(os.path.dirname(video_path), f"{os.path.splitext(os.path.basename(video_path))[0]}.mp4")
            video_path = convert_video_to_mp4(video_path, converted_path)
            video_url = get_link(video_path) or f"{base_url}/videos/{os.path.basename(converted_path)}"

        # Extract metadata
        metadata = extract_video_metadata(video_path)
        
        # Video properties
        filename = os.path.splitext(os.path.basename(video_path))[0]
        ext = 'mp4'
        thumbnail_path = os.path.join(os.path.dirname(video_path), 'thumbnail.jpg')
        captions_path = os.path.join(os.path.dirname(video_path), 'captions.srt')
        
        # Generate URLs
        thumbnail_url = get_link(thumbnail_path) or f"{base_url}/videos/{filename}/thumbnail.jpg"
        captions_url = get_link(captions_path) if os.path.exists(captions_path) else ''

        # Generate fields
        title = metadata.get('title') or generate_with_bigbird(f"Video of {filename.replace('-', ' ')}", task="title")
        description = metadata.get('description') or generate_with_bigbird(f"Video of {filename.replace('-', ' ')}", task="description")
        caption = metadata.get('caption') or generate_with_bigbird(f"Video of {filename.replace('-', ' ')}", task="caption")
        keywords_str = metadata.get('keywords') or f"video, {filename.replace('-', ', ')}, physics, experiment"
        transcript = metadata.get('transcript') or ""

        # Construct info.json
        info_json = {
            "id": filename,
            "title": title,
            "description": description,
            "keywords_str": keywords_str,
            "thumbnail_url": thumbnail_url,
            "contentUrl": video_url,
            "video_url": video_url,
            "optimized_video_url": video_url,
            "ext": ext,
            "mime_type": "video/mp4",
            "category": "Education",
            "publication_date": metadata.get('date') or "2025-04-19",
            "file_metadata": {
                "resolution": f"{metadata.get('width', 1280)}x{metadata.get('height', 720)}",
                "format": ext,
                "file_size_mb": float(metadata.get('file_size', '0KB').replace('KB', '')) / 1024
            },
            "transcript": transcript,
            "captions": captions_url,
            "schema_markup": {
                "context": "https://schema.org",
                "type": "VideoObject",
                "name": title,
                "description": description,
                "thumbnailUrl": thumbnail_url,
                "duration": f"PT{int(metadata.get('duration', 0))}S",
                "uploadDate": metadata.get('date') or "2025-04-19",
                "contentUrl": video_url,
                "keywords": keywords_str,
                "accessibilityFeature": ["captions"]
            },
            "social_meta": {
                "og:title": title,
                "og:description": description,
                "og:image": thumbnail_url,
                "og:video": video_url,
                "twitter:card": "player",
                "twitter:title": title,
                "twitter:description": description,
                "twitter:image": thumbnail_url
            }
        }

        # Save info.json
        output_path = os.path.join(output_dir, 'info.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(info_json, f, indent=2, ensure_ascii=False)
        print(f"info.json saved to {output_path}")

        # Clean up
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        return info_json


def main():
    videos_dir = os.getcwd() #"/var/www/typicallyoutliers/frontend/public/repository"
    for folder in os.listdir(videos_dir):
        video_dir = os.path.join(videos_dir, folder)
        if os.path.isdir(video_dir):
            for file in os.listdir(video_dir):
                if file.endswith(('.mp4', '.webm', '.mkv', '.avi', '.mov', '.wmv', '.flv')):
                    video_path = os.path.join(video_dir, file)
                    input(generate_video_info_json(video_path, video_dir))
main()
