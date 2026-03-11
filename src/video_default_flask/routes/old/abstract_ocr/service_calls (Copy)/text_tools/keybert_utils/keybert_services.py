from ..routes import *

def get_keybert(full_text,
                keyphrase_ngram_range=None,
                top_n=None,
                stop_words=None,
                use_mmr=None,
                diversity=None):
    keyphrase_ngram_range = keyphrase_ngram_range or (1,3),
    top_n = top_n or 10,
    stop_words = stop_words or "english",
    use_mmr = use_mmr or True,
    diversity = diversity or 0.5
    keybert = kw_model.extract_keywords(
        full_text,
        keyphrase_ngram_range=keyphrase_ngram_range,
        stop_words=stop_words,
        top_n=top_n,
        use_mmr=use_mmr,
        diversity=diversity
    )
    return keybert
def extract_keywords_nlp(text, top_n=10):
    if not isinstance(text,str):
        logger.info(f"this is not a string: {text}")
    doc = nlp(str(text))
    word_counts = Counter(token.text for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2)
    entity_counts = Counter(ent.text.lower() for ent in doc.ents if len(ent.text.split()) > 1)
    top_keywords = [word for word, _ in (word_counts + entity_counts).most_common(top_n)]
    return top_keywords

def refine_keywords(
                    full_text=None,
                    keywords=None,
                     keyphrase_ngram_range=None,
                     top_n=None,
                     stop_words=None,
                     use_mmr=None,
                     diversity=None,
                    info_data={}):
    keywords  =  keywords or extract_keywords_nlp(full_text, top_n=top_n)
    keybert = get_keybert(full_text,
                keyphrase_ngram_range=keyphrase_ngram_range,
                top_n=top_n,
                stop_words=stop_words,
                use_mmr=use_mmr,
                diversity=diversity)
    combined_keywords = list({kw for kw,_ in keybert} | set(keywords))[:10]
    keyword_density = calculate_keyword_density(full_text, combined_keywords)
    return keywords,combined_keywords,keyword_density
def calculate_keyword_density(text, keywords):
    if text:
        words = text.lower().split()
        return {kw: (words.count(kw.lower()) / len(words)) * 100 for kw in keywords if kw and len(words) > 0}
