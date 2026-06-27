from abstract_database import (
    execute_query,
    insert_any_combo,
    fetch_any_combo_,
    update_any_combo,
    connectionManager,
    create_connection
)
from abstract_utilities import get_env_value

# Registry: single source of truth for DB availability
DB_AVAILABLE = False

ENV_VARS = [
    "ABSTRACT_DATABASE_USER",
    "ABSTRACT_DATABASE_PORT",
    "ABSTRACT_DATABASE_DBNAME",
    "ABSTRACT_DATABASE_HOST",
    "ABSTRACT_DATABASE_PASSWORD",
]

def init_db(env_vars=None):
    """
    Attempts to establish a DB connection and create the videos table.
    Returns True if successful, False if anything fails.
    Sets the module-level DB_AVAILABLE flag accordingly.
    """
    global DB_AVAILABLE
    env_vars = env_vars or ENV_VARS

    env_values = {key.split('_')[-1].lower(): get_env_value(key) for key in env_vars}

    missing = [k for k, v in env_values.items() if not v]
    if missing:
        print(f"[db] Missing env vars: {missing}. DB disabled.")
        DB_AVAILABLE = False
        return False

    try:
        create_connection(**env_values)
        execute_query("""
            CREATE TABLE IF NOT EXISTS videos (
                id SERIAL PRIMARY KEY,
                video_id TEXT UNIQUE NOT NULL,
                info JSONB,
                metadata JSONB,
                whisper JSONB,
                captions JSONB,
                thumbnails JSONB,
                total_info JSONB,
                aggregated JSONB,
                seodata JSONB,
                audio_path TEXT,
                audio_format TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """, fetch=False)
        DB_AVAILABLE = True
        return True
    except Exception as e:
        print(f"[db] Failed to initialize: {e}. DB disabled.")
        DB_AVAILABLE = False
        return False


def upsert_video(video_id: str, **fields):
    if not DB_AVAILABLE:
        return None
    existing = fetch_any_combo_(
        table_name="videos",
        search_map={"video_id": video_id},
    )
    if existing:
        return update_any_combo(
            table_name="videos",
            update_map={**fields, "updated_at": "NOW()"},
            search_map={"video_id": video_id},
        )
    return insert_any_combo(
        table_name="videos",
        insert_map={"video_id": video_id, **fields},
    )


def get_video_db_record(video_id: str, hide_audio: bool = True) -> dict | None:
    if not DB_AVAILABLE:
        return None
    rows = fetch_any_combo_(
        table_name="videos",
        search_map={"video_id": video_id},
    )
    if not rows:
        return None
    record = rows[0]
    if hide_audio and "audio" in record:
        record["audio"] = f"<{len(record['audio'])} bytes>" if record["audio"] else None
    return record



##
