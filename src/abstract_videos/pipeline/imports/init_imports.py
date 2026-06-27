# at top:
import portalocker,fasteners,os
from dataclasses import dataclass
from abstract_webtools import (
    VideoDownloader,
    download_image,
    get_thumbnails,
    optimize_video_for_safari,
    download_video,dl_video,
    get_video_info,
    get_corrected_url,
    get_video_id,
    for_dl_video
    )
from abstract_utilities import *
from abstract_hugpy import *
import numpy as np
from pydub import AudioSegment
from abstract_react import getInfo,get_meta_info
get_pydub("AudioSegment")
