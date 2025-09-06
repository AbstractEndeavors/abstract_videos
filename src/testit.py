import os

from abstract_videos import *

def if_none_get_default(obj=None, default=None):
    if obj is None:
        obj = default
    return obj


input_video = "/home/computron/Desktop/solcatcher_build (2)/video_trys/Carl Sagan - THE sentence !.flv"
output_dir = "/home/computron/Desktop/solcatcher_build (2)/video_trys/output"
new_filename = generate_file_id(input_video)
output_path = os.path.join(output_dir, new_filename)
ext = '.mp4'
output_path = os.path.join(output_dir,f"{new_filename}{ext}")
print(f"input_video = {input_video}")
print(f"output_dir = {output_dir}")
print(f"output_path = {output_path}")
# Initialize pipeline
pipeline_mgr = VideoTextPipeline(
    video_path=input_video,
    output_dir=output_dir,
    output_option="copy",
    output_path=output_path,
    frame_interval=1,
    reencode=True  # Force reencode for .flv
)

# Run pipeline

texts = pipeline_mgr.run()
print("Extracted texts:", texts)
print(f"Output video saved to: {output_path}")
