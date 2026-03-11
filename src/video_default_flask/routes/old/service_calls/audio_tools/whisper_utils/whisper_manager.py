import os
import logging
from typing import Any, Dict, Optional

from .whisper_call_schema import get_whisper_input_keys, get_whisper_bool_key
from .routes import get_key_vars, get_video_info_path
from .whisper_pipeline import WhisperPipeline
from abstract_utilities import safe_dump_to_file, safe_load_from_json

logger = logging.getLogger(__name__)


class WhisperManager:
    """
    Orchestrates the Whisper transcription step with three levels of idempotency:
      - Persistent skip if existing info.json contains segments
      - Runtime skip if already ran once in this Python process
      - Force override when requested
    Additionally ensures segments are generated and an SRT file is created.
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

        # 2) Check if transcription is requested
        run_flag, info_data = self.should_run(req=req, info_data=info_data)
        if not run_flag and not force:
            logger.info("[WhisperManager] skipping: transcription not requested")
            return info_data

        # 3) Persistent skip if existing file has segments and not forced
        info_path = get_video_info_path(**info_data)
        if os.path.exists(info_path) and not force:
            logger.info(f"[WhisperManager] found existing file {info_path!r}")
            existing_data = safe_load_from_json(info_path)
            if existing_data.get('segments'):
                logger.info("[WhisperManager] skipping: existing info.json contains segments")
                pipeline = WhisperPipeline(existing_data)
                pipeline.export_srt()
                return existing_data
            else:
                logger.info("[WhisperManager] existing info.json missing 'segments', re-running transcription")
                # Merge existing meta and continue to run
                info_data.update(existing_data)

        # 4) Runtime skip if we've already run once and not forced
        if self._has_run and not force:
            logger.info("[WhisperManager] skipping: already ran once in this process")
            return info_data

        # 5) Run the pipeline
        pipeline = WhisperPipeline(info_data)
        result = pipeline.run()

        # 6) Warn if no segments generated
        if not result.get('segments'):
            logger.warning("[WhisperManager] transcription result missing 'segments'")

        # 7) Merge results and persist info.json
        info_data.update(result)
        safe_dump_to_file(data=info_data, file_path=info_path)
        self._has_run = True

        # 8) Export SRT captions
        pipeline.export_srt()
        logger.info("[WhisperManager] SRT captions file created")

        logger.info(f"[WhisperManager] transcription completed and saved to {info_path!r}")
        return info_data
