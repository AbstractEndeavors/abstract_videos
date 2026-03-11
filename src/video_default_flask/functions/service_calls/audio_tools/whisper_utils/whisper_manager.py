import os
import logging
from typing import Any, Dict, Optional

from .whisper_call_schema import get_whisper_input_keys, get_whisper_bool_key
from .routes import get_key_vars, get_video_info_path
from .whisper_pipeline import WhisperPipeline
from abstract_utilities import safe_dump_to_file

logger = logging.getLogger(__name__)


class WhisperManager:
    """
    Orchestrates the Whisper transcription step with two levels of idempotency:
      - Persistent skip (if info.json already exists on disk)
      - Runtime skip (if already ran once in this Python process)
    """
    def __init__(self):
        self._has_run: bool = False

    def fetch_vars(
        self,
        req: Any = None,
        info_data: Optional[Dict[str, Any]] = None
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        keys = get_whisper_input_keys()
        return get_key_vars(keys, req=req, info_data=info_data)

    def should_run(
        self,
        req: Any = None,
        info_data: Dict[str, Any] = {}
    ) -> tuple[bool, Dict[str, Any]]:
        return get_whisper_bool_key(req=req, info_data=info_data)

    def run(
        self,
        req: Any = None,
        info_data: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        info_data = info_data or {}

        # 1) Gather inputs
        _, info_data = self.fetch_vars(req=req, info_data=info_data)

        # 2) Check if user even wants to run
        run_flag, info_data = self.should_run(req=req, info_data=info_data)
        if not run_flag:
            logger.info("[WhisperManager] skipping: transcription not requested")
            return info_data

        # 3) Persistent skip: if info.json exists on disk
        path = get_video_info_path(**info_data)
        if os.path.exists(path) and not force:
            logger.info(f"[WhisperManager] skipping: found existing {path!r}")
            return info_data

        # 4) Runtime skip: if we've already run in this session
        if self._has_run and not force:
            logger.info("[WhisperManager] skipping: already ran once in this process")
            return info_data

        # 5) Actually run the pipeline
        pipeline = WhisperPipeline(info_data)
        result = pipeline.run()

        # 6) Merge results and persist
        info_data.update(result)
        safe_dump_to_file(data=info_data, file_path=path)
        self._has_run = True

        logger.info(f"[WhisperManager] transcription completed and saved to {path!r}")
        return info_data
