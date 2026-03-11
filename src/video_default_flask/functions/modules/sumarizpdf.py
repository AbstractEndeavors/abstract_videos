import logging

class InfoErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # only allow INFO or ERROR (you can add CRITICAL here if you like)
        return record.levelno in (logging.INFO, logging.ERROR)

# grab the root logger (or any named logger you want)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)   # let all records reach your handlers…

# clear out any existing handlers if you like
for h in list(logger.handlers):
    logger.removeHandler(h)

# console handler: attach our filter
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)        # handler level must be low enough to see INFO & ERROR
ch.addFilter(InfoErrorFilter())
fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
ch.setFormatter(fmt)
logger.addHandler(ch)

# now only INFO and ERROR will print to console:
logger.debug("won’t show")
logger.info("➡️ this shows")
logger.warning("won’t show")
logger.error("❌ this shows")
logger.critical("❌ this shows too, because it’s >= ERROR")
import os
import json
import pdfplumber
import spacy
import hashlib
import signal
import shutil
##from keybert import KeyBERT
##from transformers import pipeline, T5Tokenizer
from abstract_hugpy.hugpy_console.hugging_face_models import *
from abstract_hugpy.hugpy_console.hugging_face_models.summarizer_model import *
from abstract_hugpy.hugpy_console.hugging_face_models.keybert_model import *

from collections import Counter
from pdf2image import convert_from_path
import pytesseract
import PyPDF2
from abstract_utilities import make_dirs, safe_dump_to_file,safe_read_from_json
from transformers import T5ForConditionalGeneration, T5Tokenizer, GenerationConfig

# ——— Configuration —————————————————————————————————————
PDFS_DIR = '/var/www/typicallyoutliers/frontend/public/repository/new_pdfs'

# ——— Logging Setup —————————————————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(process)d - %(levelname)s - %(filename)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler("pdf_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.propagate = False

# ——— Initialize Models —————————————————————————————————
try:
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")
    tokenizer = get_tokenizer()#T5Tokenizer.from_pretrained("t5-small")
    keyword_extractor = pipeline("feature-extraction", model="distilbert-base-uncased")
    kw_model = get_keybert_model()#KeyBERT(model=keyword_extractor.model)
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"initialize_models - Failed to load models: {e}")
    raise

# ——— Signal Handler for Interruptions ——————————————————
def handle_interrupt(signalnum, frame):
    logger.info(f"handle_interrupt - Received interrupt signal {signalnum}, cleaning up")
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_interrupt)

def compute_file_hash(filepath: str, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a file."""
    try:
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.error(f"compute_file_hash - Failed to hash {filepath}: {e}")
        return ""

def check_duplicate_pdf(pdf_path: str, processed_hashes: set) -> bool:
    """Check if PDF has been processed by comparing hashes."""
    file_hash = compute_file_hash(pdf_path)
    if file_hash in processed_hashes:
        logger.info(f"check_duplicate_pdf - Duplicate PDF detected: {pdf_path}")
        return True
    processed_hashes.add(file_hash)
    return False

def estimate_token_length(text: str) -> int:
    """Estimate token length using the model's tokenizer."""
    try:
        tokens = tokenizer.encode(text, add_special_tokens=True)
        logger.debug(f"estimate_token_length - Estimated {len(tokens)} tokens for text of {len(text)} characters")
        return len(tokens)
    except Exception as e:
        logger.error(f"estimate_token_length - Failed: {e}")
        return len(text.split()) // 1.3

def chunk_text(text: str, max_tokens: int = 512) -> list:
    """Chunk text into segments within token limit."""
    try:
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        for word in words:
            word_tokens = len(word) // 4 + 1
            if current_length + word_tokens > max_tokens:
                chunk_text = " ".join(current_chunk)
                if estimate_token_length(chunk_text) <= max_tokens:
                    chunks.append(chunk_text)
                else:
                    sub_chunks = chunk_text_by_sentences(chunk_text, max_tokens)
                    chunks.extend(sub_chunks)
                current_chunk = [word]
                current_length = word_tokens
            else:
                current_chunk.append(word)
                current_length += word_tokens
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if estimate_token_length(chunk_text) <= max_tokens:
                chunks.append(chunk_text)
            else:
                sub_chunks = chunk_text_by_sentences(chunk_text, max_tokens)
                chunks.extend(sub_chunks)
        logger.info(f"chunk_text - Created {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"chunk_text - Failed: {e}")
        return [text]

def chunk_text_by_sentences(text: str, max_tokens: int) -> list:
    """Split text by sentences if a chunk is still too long."""
    try:
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        chunks = []
        current_chunk = []
        current_length = 0
        for sent in sentences:
            sent_tokens = estimate_token_length(sent)
            if current_length + sent_tokens > max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sent]
                current_length = sent_tokens
            else:
                current_chunk.append(sent)
                current_length += sent_tokens
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks
    except Exception as e:
        logger.error(f"chunk_text_by_sentences - Failed: {e}")
        return [text]

def extract_pdf_text(pdf_path: str, min_text_length: int = 50) -> str:
    """Extract text from a PDF file, falling back to OCR if needed."""
    try:
        if not os.path.isfile(pdf_path):
            logger.error(f"extract_pdf_text - PDF not found: {pdf_path}")
            return ""
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                if not page.cropbox:
                    page.cropbox = page.mediabox
                    logger.info(f"extract_pdf_text - Set CropBox to MediaBox for page in {pdf_path}")
                full_text += (page.extract_text() or "") + " "
        
        if full_text.strip() and len(full_text) >= min_text_length:
            logger.info(f"extract_pdf_text - Extracted {len(full_text)} characters from {pdf_path} using pdfplumber")
            return full_text.strip()
        
        logger.info(f"extract_pdf_text - Minimal text extracted ({len(full_text)}), attempting OCR for {pdf_path}")
        images = convert_from_path(pdf_path, first_page=1, last_page=10, timeout=30)
        full_text = " ".join(pytesseract.image_to_string(img, lang='eng', config='--psm 6') for img in images)
        if not full_text.strip():
            logger.error(f"extract_pdf_text - OCR extracted no text from {pdf_path}")
            return ""
        logger.info(f"extract_pdf_text - Extracted {len(full_text)} characters from {pdf_path} using OCR")
        return full_text.strip()
    except Exception as e:
        logger.error(f"extract_pdf_text - Failed to extract text from {pdf_path}: {e}")
        return ""

def extract_keywords_nlp(text: str, top_n: int = 10) -> list:
    """Extract keywords using spaCy."""
    try:
        doc = nlp(text)
        word_counts = Counter(token.text for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2)
        entity_counts = Counter(ent.text.lower() for ent in doc.ents if len(ent.text.split()) > 1)
        top_keywords = [word for word, _ in (word_counts + entity_counts).most_common(top_n)]
        logger.info(f"extract_keywords_nlp - Extracted {len(top_keywords)} spaCy keywords")
        return top_keywords
    except Exception as e:
        logger.error(f"extract_keywords_nlp - Failed: {e}")
        return []

def calculate_keyword_density(text: str, keywords: list) -> dict:
    """Calculate keyword density in text."""
    try:
        text_words = text.lower().split()
        total_words = len(text_words)
        density = {}
        for keyword in keywords:
            count = sum(1 for word in text_words if keyword.lower() in word)
            density[keyword] = (count / total_words) * 100 if total_words > 0 else 0
        logger.info(f"calculate_keyword_density - Calculated density for {len(keywords)} keywords")
        return density
    except Exception as e:
        logger.error(f"calculate_keyword_density - Failed: {e}")
        return {}

def generate_title(keywords: list, max_length: int = 70) -> str:
    """Generate a title using top keywords."""
    try:
        if not keywords:
            return "Untitled Document"
        top_keywords = keywords[:3]
        title = f"{top_keywords[0].title()} - {' and '.join(k.title() for k in top_keywords[1:])} Overview"
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        logger.info(f"generate_title - Generated title: {title}")
        return title
    except Exception as e:
        logger.error(f"generate_title - Failed: {e}")
        return "Untitled Document"

def process_pdf(pdf_path: str, output_dir: str = None, processed_hashes: set = None,json_data={}) -> dict:
    """Summarize a PDF, extract keywords, and generate a title."""
    processed_hashes = processed_hashes or set()

    try:
        # Check for duplicates
        if check_duplicate_pdf(pdf_path, processed_hashes):
            json_data['status'] = "Duplicate PDF, skipped"
            return json_data

        # Extract text
        full_text = extract_pdf_text(pdf_path)
        if not full_text:
            json_data['status'] = "No text extracted"
            return json_data
        

        json_data['full_text'] = full_text
        info_path = json_data.get('info_path') or json_data.get('page_info_path')
        if info_path and os.path.isfile(info_path):
            prev_info = safe_read_from_json(info_path) or {}
            prev_full_text = prev_info.get('full_text')
            if prev_full_text == full_text:
                prev_info['prev_info'] = True
                return prev_info
        
        # Keyword extraction with KeyBERT
        keywords = refine_keywords(
            full_text=full_text,
            keyphrase_ngram_range=(1, 3),
            stop_words='english',
            top_n=10,
            use_mmr=True,
            diversity=0.5
        )
        json_data.update(keywords)
##        # spaCy-based keywords
##        json_data['keywords'] = extract_keywords_nlp(full_text, top_n=10)
##
##        # Combine keywords
##        combined_keywords = list(set([kw[0] for kw in keywords] + json_data['keywords']))
##        json_data['combined_keywords'] = combined_keywords[:10]
##
##        # Calculate keyword density
##        json_data['keyword_density'] = calculate_keyword_density(full_text, combined_keywords)

        # Generate summary
        if full_text:
            chunks = chunk_text(full_text, max_tokens=512)
            summaries = []
            for chunk in chunks:
                input_length = estimate_token_length(chunk)
                max_length = min(input_length // 2, 150)
                summary = summarizer(chunk, max_length=max_length, min_length=40, truncation=True)[0]['summary_text']
                summaries.append(summary)
            full_summary = " ".join(summaries)
            if estimate_token_length(full_summary) > 512:
                full_summary = summarizer(full_summary, max_length=160, min_length=40, truncation=True)[0]['summary_text']
            primary_keywords = [kw[0] for kw in json_data['keywords_keybert'] if kw[1] > 0.8]
            for kw in primary_keywords:
                if kw.lower() not in full_summary.lower():
                    full_summary += f" Includes {kw}."
            json_data['summary'] = full_summary
        
        # Generate title
        json_data['seo_title'] = generate_title(json_data['combined_keywords'])
        return json_data
    except Exception as e:
        logger.error(f"process_pdf - Failed for {pdf_path}: {e}")
        json_data['status'] = f"Error: {e}"
        return json_data

def cleanup_page_files(output_dir: str, filename: str, ext: str):
    """Delete all page files for a given PDF."""
    try:
        page_files = [f for f in os.listdir(output_dir) if f.startswith(f"{filename}_page_") and f.endswith(ext)]
        for page_file in page_files:
            page_path = os.path.join(output_dir, page_file)
            try:
                os.remove(page_path)
                logger.info(f"cleanup_page_files - Deleted page file: {page_path}")
            except Exception as e:
                logger.error(f"cleanup_page_files - Failed to delete {page_path}: {e}")
    except Exception as e:
        logger.error(f"cleanup_page_files - Failed to clean up pages in {output_dir}: {e}")

def process_page(page, page_path):
    """Write a single PDF page to a file."""
    try:
        if not os.path.isfile(page_path):
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(page)
            with open(page_path, 'wb') as f:
                pdf_writer.write(f)
            logger.info(f"process_page - Created page file: {page_path}")
        logger.info(f"existing_page -page file: {page_path} already exists")
    except Exception as e:
        logger.error(f"process_page - Failed to create page file {page_path}: {e}")
        raise

def split_pdf(pdf_path):
    """Split a PDF into pages."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        pages = pdf_reader.pages
        logger.info(f"split_pdf - Loaded {len(pages)} pages from {pdf_path}")
        return pages
    except Exception as e:
        logger.error(f"split_pdf - Failed to load {pdf_path}: {e}")
        raise
def change_pdf_pages(json_data):
    pdf_pages_dir = make_dirs(json_data['pages_dir'])
    dirname = os.path.dirname(pdf_pages_dir)
    pdf_pages_old = os.path.join(dirname,'pdf_pages')
    if os.path.exists(pdf_pages_old):
        pdf_paths = [os.path.join(pdf_pages_old,item) for item in os.listdir(pdf_pages_old)]
        for pdf_path in pdf_paths:
            pdf_basename = os.path.basename(pdf_path)
            pdf_filename,pdf_ext = os.path.splitext(pdf_basename)
            pdf_index = pdf_filename.split('_')[-1]
            pdf_page_dir = f"page_{pdf_index}"
            new_pdf_page_dir = os.path.join(pdf_pages_dir,pdf_page_dir)
            make_dirs(new_pdf_page_dir)
            shutil.move(pdf_path,new_pdf_page_dir)
def split_into_pages(pdf_path: str, output_dir: str = None,json_data={}) -> list:
    """Split a PDF into individual pages and process each."""
    filename = json_data['filename']
    info_path = json_data['info_path']
    if info_path and os.path.isfile(info_path):
        json_data = safe_read_from_json(info_path)
    all_pages = json_data.get('all_pages',[])
    json_data['all_pages'] = all_pages
    processed_hashes = set()
    pdf_pages_dir = make_dirs(json_data['pages_dir'])

    try:
        pages = split_pdf(pdf_path)
        json_data['num_pages'] = len(pages)
        logger.info(f"split_into_pages - Processing {json_data['filename']} with {json_data['num_pages']} pages")
        
        for i, page in enumerate(pages):
            i_index = i+1
            page_info = {'page_number':i,"page_index_number":i_index}
            page_dirbase = f"page_{i_index}"
            pdf_page_dir = os.path.join(pdf_pages_dir,page_dirbase)
            os.makedirs(pdf_page_dir,exist_ok=True)
            page_filename = f"{filename}_{page_dirbase}"
            page_info['page_filename'] = page_filename
            page_info['page_pdf_basename'] = f"{page_filename}.pdf"
            page_info['page_txt_basename'] = f"{page_filename}.txt"

            page_pdf_path = os.path.join(pdf_page_dir, page_info['page_pdf_basename'])
            page_txt_path = os.path.join(pdf_page_dir, page_info['page_txt_basename'])
            page_info_path = os.path.join(pdf_page_dir, 'info.json')
            page_info['page_info_path'] = page_info_path
            try:
               
                logger.info(f"split_into_pages - Processing page {i_index} of {json_data['num_pages']}")
                
                process_page(page, page_pdf_path)
                
                page_info = process_pdf(page_pdf_path,
                                        output_dir=output_dir,
                                        processed_hashes=processed_hashes,
                                        json_data=page_info)
                if not page_info.get('prev_info'):
                    page_info['prev_info'] = True
                    write_to_file(contents=page_info['full_text'], file_path=page_txt_path)
                    safe_dump_to_file(data=page_info, file_path=page_info_path)
                    json_data['all_pages'].append(page_info)
                    
            except Exception as e:
                logger.error(f"split_into_pages - Failed to process page {i_index} of {pdf_path}: {e}")
                json_data['all_pages'].append({'pdf_path': pdf_path, 'page_number': i_index, 'status': f"Error: {e}"})
            finally:
                if json_data['flat_directory']:
                    for page_path in [page_pdf_path,page_txt_path]:
                        if page_path and os.path.exists(page_path):
                            try:
                                os.remove(page_path)
                                logger.info(f"split_into_pages - Deleted page file: {page_path}")
                            except Exception as e:
                                logger.error(f"split_into_pages - Failed to delete {page_path}: {e}")

                
        # Final cleanup
        if json_data['flat_directory']:
            cleanup_page_files(pdf_pages_dir, filename, '.pdf')
        # Save all page data as a list of JSON objects
        safe_dump_to_file(data=json_data, file_path=info_path)
        logger.info(f"split_into_pages - Saved all pages info to {json_data['info_path']}")        

        
        return json_data
    except KeyboardInterrupt:
        logger.info(f"split_into_pages - Interrupted during processing of {pdf_path}")
        raise
    except Exception as e:
        logger.error(f"split_into_pages - Failed for {pdf_path}: {e}")
        return json_data
    finally:
        if json_data['flat_directory']:
            cleanup_page_files(pdf_pages_dir, json_data['filename'], '.pdf')
def compile_document_analysis(json_data):
    """
    Combine all page-level results into a single document-level analysis.
    """
##    try:
    info_path = json_data.get("info_path")
    text_path = json_data.get("text_path")
    pdf_directory = json_data.get('pdf_directory')
    filename = json_data.get('filename')
    all_pages = json_data.get("all_pages", [])
    if not all_pages:
        logger.warning("compile_document_analysis - No pages to compile.")
        return json_data

    # 1️⃣  Gather full text and all per-page summaries
    all_texts = []
    all_summaries = []
    for page in all_pages:
        text = page.get("full_text", "")
        summary = page.get("summary", "")
        if text:
            all_texts.append(text)
        if summary:
            all_summaries.append(summary)

    full_text = " ".join(all_texts).strip()
    if not text_path:
        text_path = os.path.join(pdf_directory,f"{filename}.txt")
        json_data['text_path'] = text_path
    if text_path and not os.path.isfile(text_path):
        write_to_file(contents=full_text,file_path=text_path)
    info_path = json_data.get('info_path') or json_data.get('page_info_path')
    if info_path and os.path.isfile(info_path):
        prev_info = safe_read_from_json(info_path) or {}
        prev_full_text = prev_info.get('document_full_text')
        if prev_full_text == full_text:
            prev_info['prev_info'] = True
            return prev_info
    full_summary_text = " ".join(all_summaries).strip() or full_text[:2000]

    # 2️⃣  Extract global keywords
    combined_keywords = refine_keywords(
        full_text=full_text,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        top_n=15,
        use_mmr=True,
        diversity=0.5,
    )
    json_data.update(combined_keywords)

    # 3️⃣  Summarize the entire document
    chunks = chunk_text(full_summary_text, max_tokens=512)
    doc_summaries = []
    for chunk in chunks:
        input_len = estimate_token_length(chunk)
        max_len = min(input_len // 2, 200)
        try:
            summ = summarizer(
                chunk,
                max_length=max_len,
                min_length=40,
                truncation=True
            )[0]["summary_text"]
            doc_summaries.append(summ)
        except Exception as e:
            logger.error(f"compile_document_analysis - Summarizer failed: {e}")
            doc_summaries.append(chunk[:500])
    final_summary = " ".join(doc_summaries)

    # 4️⃣  Build a title
    key_list = [kw[0] for kw in json_data.get("keywords_keybert", [])[:5]]
    seo_title = generate_title(key_list)

    # 5️⃣  Update master JSON
    json_data["document_full_text"] = full_text
    json_data["document_summary"] = final_summary
    json_data["document_title"] = seo_title
    json_data["num_pages"] = len(all_pages)
    json_data["status"] = "Document compiled successfully"
    
    
    if info_path:
        safe_dump_to_file(json_data, info_path)
        logger.info(f"compile_document_analysis - Saved compiled info to {info_path}")

    return json_data

##    except Exception as e:
##        logger.error(f"compile_document_analysis - Failed: {e}")
##        json_data["status"] = f"Error during document compilation: {e}"
##        return json_data


from abstract_utilities.path_utils import *
def main(directory,pdf_directory=True):
    processed_hashes = set()
    dirs,files = get_files_and_dirs(directory=directory,allowed_exts=['.pdf'])
    for pdf_path in files:
        file_parts = get_file_parts(pdf_path)
        json_data = {'flat_directory':False}
        dirname = file_parts.get('dirname')
        filename = file_parts.get('filename')
        basename = file_parts.get('basename')
        dirbase = file_parts.get('dirbase')
        parent_dirname = file_parts.get('parent_dirname')
        parent_dirbase = file_parts.get('parent_dirbase')
        super_dirname = file_parts.get('super_dirname')
        super_dirbase = file_parts.get('super_dirbase')
        json_data['file_parts'] = file_parts
        if not dirbase.startswith('page_') and parent_dirbase != 'pages' and not basename.startswith(super_dirbase):

            if pdf_directory:
                pdf_nudirectory = dirname
                if pdf_directory == True:
                    if dirbase != filename:
                       pdf_nudirectory = os.path.join(dirname,filename)
                else:
                    pdf_nudirectory = os.path.join(pdf_directory,filename)
                os.makedirs(pdf_nudirectory,exist_ok=True)
                pdf_nupath = os.path.join(pdf_nudirectory,basename)
                if not os.path.isfile(pdf_nupath):
                    shutil.move(pdf_path,pdf_nupath)
                    if os.path.isfile(pdf_path):
                        os.remove(pdf_path)
                pdf_path = pdf_nupath
                dirname  = pdf_nudirectory
            else:
               json_data['flat_directory'] = True
              
            json_data['filename'] = filename
            json_data['pdf_directory']  = dirname
            json_data['pdf_basename'] = basename
            json_data['pdf_path'] = pdf_path
            json_data['info_path'] = os.path.join(json_data.get('pdf_directory'),'info.json')
            json_data['text_path'] = os.path.join(json_data.get('pdf_directory'),f"{filename}.txt")  
            pages_dir = dirname
            pages_dir = os.path.join(dirname,'pages')
            json_data['pages_dir'] = pages_dir
            change_pdf_pages(json_data)
               
            
            all_pages_info_json = os.path.join(dirname,'all_pages_info.json')
            info_json = os.path.join(dirname,'info.json')
    ##        for info_json in [info_json,all_pages_info_json]:
    ##            if os.path.isfile(info_json):
    ##                os.remove(info_json)
    ##        for each_dir in [text_dir,pages_dir]:
    ##            if os.path.isdir(each_dir):
    ##                shutil.rmtree(each_dir)
    ##            if os.path.isfile(each_dir):
    ##                os.remove(each_dir)
                
            try:
                logger.info(f"main - Processing PDF: {pdf_path}")
                json_data = split_into_pages(pdf_path, dirname, json_data)
                json_data = compile_document_analysis(json_data)
                logger.info(f"compile_document_analysis - Completed for {json_data['filename']}")
            except Exception as e:
                logger.error(f"main - Failed to process {pdf_path}: {e}")

if __name__ == "__main__":
    main(directory="/var/www/presites/thedailydialectics/react/main/public/pdfs")
