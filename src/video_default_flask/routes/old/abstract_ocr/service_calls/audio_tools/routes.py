from ..routes import *
from .whisper_manager import WhisperManager

whisper_mgr = WhisperManager()

@app.route("/transcribe", methods=["POST"])
def transcribe():
    req = request
    info = load_existing_info_for(req)
    updated = whisper_mgr.run(req=req, info_data=info)
    return jsonify(updated)
