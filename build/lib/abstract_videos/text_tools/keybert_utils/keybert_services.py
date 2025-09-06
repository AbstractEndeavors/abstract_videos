from ..routes import *
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def get_keybert(full_text, keyphrase_ngram_range=None, top_n=None, stop_words=None, use_mmr=None, diversity=None):
    keyphrase_ngram_range = keyphrase_ngram_range or (1, 2)  # Reduced max n-gram range
    top_n = top_n or 5  # Reduced top_n
    stop_words = stop_words or "english"
    use_mmr = use_mmr or True
    diversity = diversity or 0.6  # Increased diversity for less overlap
    keybert = kw_model.extract_keywords(
        full_text,
        keyphrase_ngram_range=keyphrase_ngram_range,
        stop_words=stop_words,
        top_n=top_n * 2,  # Extract more initially for filtering
        use_mmr=use_mmr,
        diversity=diversity
    )
    # Filter by score threshold (e.g., > 0.3) to keep high-relevance keywords
    filtered_keybert = [(kw, score) for kw, score in keybert if score > 0.3][:top_n]
    return filtered_keybert
def extract_keywords_nlp(text, top_n=5):  # Reduced top_n
    doc = nlp(str(text))
    if not isinstance(text, str):
        logger.info(f"this is not a string: {text}")
    # Focus on NOUN, PROPN, and multi-word entities, stricter length filter
    word_counts = Counter(token.text.lower() for token in doc 
                          if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 3)
    entity_counts = Counter(ent.text.lower() for ent in doc.ents 
                            if len(ent.text.split()) >= 2 and ent.label_ in ["PERSON", "ORG", "GPE", "EVENT"])
    # Combine and take top 5, prioritize entities
    top_keywords = [word for word, _ in (entity_counts + word_counts).most_common(top_n)]
    return top_keywords

def refine_keywords(full_text=None, keywords=None, keyphrase_ngram_range=None, top_n=None, stop_words=None, use_mmr=None, diversity=None, info_data={}):
    top_n = top_n or 5
    keywords = keywords or extract_keywords_nlp(full_text, top_n=top_n)
    keybert = get_keybert(full_text, keyphrase_ngram_range=keyphrase_ngram_range, top_n=top_n, stop_words=stop_words, use_mmr=use_mmr, diversity=diversity)
    combined_keywords = list(set(kw.lower() for kw, _ in keybert) | set(kw.lower() for kw in keywords))[:top_n]
    keyword_density = calculate_keyword_density(full_text, combined_keywords)
    if info_data:
        info_data['keywords'], info_data['combined_keywords'], info_data['keyword_density'] = keywords, combined_keywords, keyword_density
        return info_data
    return keywords, combined_keywords, keyword_density
import re

def calculate_keyword_density(text, keywords):
    if not text or not keywords:
        return {kw: 0.0 for kw in keywords} if keywords else {}
    # Split text into words, removing punctuation
    words = [word.strip(".,!?").lower() for word in re.split(r'\s+', text) if word.strip(".,!?")]
    total_words = len(words)
    if total_words == 0:
        return {kw: 0.0 for kw in keywords}
    return {kw: (words.count(kw.lower()) / total_words) * 100 for kw in keywords if kw}
