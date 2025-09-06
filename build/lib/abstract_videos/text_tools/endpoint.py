from keybert_utils.keybert_manager import KeywordManager
from summarizer_utils.summarizer_manager import SummarizerManager
kw_mgr = KeywordManager()
summ_mgr = SummarizerManager()

@app.route("/generate_keywords", methods=["POST"])
def generate_keywords():
    req = request
    info = load_existing_info_for(req)
    new_info = kw_mgr.run(req=req, info_data=info)
    return jsonify(new_info)



@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    req = request
    info = load_existing_info_for(req)
    updated = summ_mgr.run(req=req, info_data=info)
    return jsonify(updated)
