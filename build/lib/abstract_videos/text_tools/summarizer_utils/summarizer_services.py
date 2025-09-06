from ..routes import *
def chunk_summaries(chunks, max_length=None, min_length=None, truncation=True):
    max_length = max_length or 100
    min_length = min_length or 50
    summaries = []
    for idx, chunk in enumerate(chunks):
        try:
            out = summarizer(
                chunk,
                max_length=max_length,
                min_length=min_length,
                truncation=truncation
            )
            summary_text = out[0]["summary_text"]
            summaries.append(summary_text)
        except Exception as e:
            print(f"Error summarizing chunk {idx}: {e}")
            summaries.append("")  # Fallback to empty string
    return summaries

def split_to_chunk(full_text, max_words=None):
    max_words = max_words or 200
    sentences = full_text.split(". ")
    chunks, buf = [], ""
    for sent in sentences:
        if len((buf + sent).split()) <= max_words:
            buf += sent + ". "
        else:
            if buf.strip():
                chunks.append(buf.strip())
            buf = sent + ". "
    if buf.strip():
        chunks.append(buf.strip())
    return chunks

def get_summary(
    full_text,
    keywords=None,
    max_words=None,
    max_length=None,
    min_length=None,
    truncation=True
):
    summary = ""
    if full_text and summarizer:
        try:
            chunks = split_to_chunk(full_text, max_words=max_words)
            summaries = chunk_summaries(
                chunks,
                max_length=max_length,
                min_length=min_length,
                truncation=truncation
            )
            # Join summaries and enforce total word limit
            summary = " ".join(summaries).strip()
            words = summary.split()
            if len(words) > 150:
                words = words[:150]
            summary = " ".join(words) + "..."
        except Exception as e:
            print(f"Error generating summary: {e}")
            summary = ""
    return summary
