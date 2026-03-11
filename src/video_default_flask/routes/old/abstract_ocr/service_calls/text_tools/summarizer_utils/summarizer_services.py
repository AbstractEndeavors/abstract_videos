
def chunk_summaries(chunks,
                    max_length=None,
                    min_length=None,
                    truncation=False):

    max_length = max_length or 160
    min_length = min_length or 40
    summaries = []
    for idx, chunk in enumerate(chunks):
       
            out = summarizer(
                chunk,
                max_length=max_length,
                min_length=min_length,
                truncation=truncation  # >>> explicitly drop over‑long parts if still above model limit
            )
            summaries.append(out[0]["summary_text"])
   
    return summaries

def split_to_chunk(full_text,max_words=None):
    # split into sentence-ish bits
    max_words = max_words or 300
    sentences = full_text.split(". ")
    chunks, buf = [], ""
    for sent in sentences:
        # +1 for the “. ” we removed
        if len((buf + sent).split()) <= max_words:
            buf += sent + ". "
        else:
            chunks.append(buf.strip())
            buf = sent + ". "
    if buf:
        chunks.append(buf.strip())
    return chunks
def get_summary(full_text,
                keywords=None,
                max_words=None,
                max_length=None,
                min_length=None,
                truncation=False):
    summary =  None
    if full_text and summarizer:
        chunks = split_to_chunk(full_text,max_words=max_words)
        summaries = chunk_summaries(chunks,
                        max_length=max_length,
                        min_length=min_length,
                        truncation=truncation)
        # stitch back together
        summary = " ".join(summaries).strip()

    return summary
