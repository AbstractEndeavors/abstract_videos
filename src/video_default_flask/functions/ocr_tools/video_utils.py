from .functions import (VideoFileClip,
                        cv2,
                        os,
                        np)
from .ocr_utils import extract_image_texts_from_directory
def extract_video_frammes(video_path,output_directory,frame_interval=None):
    frame_interval = frame_interval or = 1
    video = VideoFileClip(video_path)
    duration = video.duration
    for t in range(0, int(duration), frame_interval):
        frame_path = os.path.join(output_directory,f"{video_id}_frame_{t}.jpg")
        if not os.path.isfile(frame_path):
            frame = video.get_frame(t)
            cv2.imwrite(frame_path, cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
def analyze_video_text(video_path,
                       output_directory=None,
                       image_texts=None,
                       remove_phrases=None,
                       video_id=None,
                       frame_interval=None):
    if video_path == None or not video_path or not os.path.isfile(video_path):
        return image_texts
    remove_phrases=remove_phrases or []
    output_directory = output_directory or os.getcwd()
    
    extract_video_frames(video_path=video_path,
                          output_directory=output_directory,
                          frame_interval=frame_interval)
    image_texts = extract_image_texts_from_directory(output_directory=output_directory,
                                                     image_texts=image_texts,
                                                     remove_phrases=remove_phrases)
    
    return image_texts
