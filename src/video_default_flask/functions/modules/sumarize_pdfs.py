import os
import glob
import json
from transformers import pipeline
from keybert import KeyBERT
from abstract_utilities import *
# ——— your existing pipelines ——————————————————————
summarizer        = pipeline("summarization", model="Falconsai/text_summarization")
keyword_extractor = pipeline("feature-extraction", model="distilbert-base-uncased")
kw_model          = KeyBERT(model=keyword_extractor.model)
generator         = pipeline("text-generation", model="distilgpt2", device=-1)

# ——— utilities —————————————————————————————————————
def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text: str, max_words: int = 500):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i : i + max_words])

# ——— summarization —————————————————————————————————
def make_summary(text: str) -> str:
    """Summarize large text by chunking + merging."""
    chunks = list(chunk_text(text, max_words=500))
    # 1) Summarize each chunk
    partial = [[
        s["summary_text"]
        for s in summarizer(chunk, max_length=150, min_length=30, do_sample=False)
    ] for chunk in chunks]
    merged = " ".join(partial)
    # 2) If we had multiple chunks, do a final pass
    if len(chunks) > 1:
        merged = summarizer(merged, max_length=150, min_length=30, do_sample=False)[0]["summary_text"]
    return merged

# ——— keyword extraction ——————————————————————————————
def extract_keywords(text: str, top_n: int = 10):
    return [kw for kw, score in kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        top_n=top_n
    )]

# ——— optional GPT refine ——————————————————————————————
def refine_with_gpt(summary: str) -> str:
    prompt = f"Write a concise abstract for the following content:\n\n{summary}\n\nAbstract:"
    out = generator(prompt, max_length=200, num_return_sequences=1)[0]["generated_text"]
    return out.split("Abstract:")[-1].strip()

# ——— driver ————————————————————————————————————————
def process_all(txt_dir: str,out_dir:str):
    out_dir = make_dirs(out_dir)
    for txt_path in glob.glob(f"{txt_dir}/**/*.txt", recursive=True):
        
        try:
            text = load_text(txt_path)
            if isinstance(text,list):
                text = '\n'.join(text)
            summary  = make_summary(text)
            keywords = extract_keywords(text)
            abstract = refine_with_gpt(summary)  # or just use `summary`
            
            result = {
                "filename":    os.path.basename(txt_path),
                "keywords":    keywords,
                "summary":     summary,
                "abstract":    abstract
            }
            # write out alongside your text file
            dirname = os.path.dirname(txt_path)
            parent_dirname = os.path.dirname(dirname)
            dirbase = os.path.basename(parent_dirname)
            new_out_dir = make_dirs(out_dir,dirbase)
            
            info_path = os.path.join(new_out_dir,'info.json')
            
            
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"{e}")
            pass
if __name__ == "__main__":
    process_all(
        txt_dir="/var/www/typicallyoutliers/frontend/public/repository/new_pdfs",
        out_dir ="/var/www/typicallyoutliers/frontend/public/repository/new_texts")
