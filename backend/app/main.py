import os
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import tempfile
from typing import List, Dict, Any, Optional
import logging
import unicodedata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import LLM capabilities (optional)
try:
    import sys
    import os
    # Add current directory to Python path to ensure llm_search can be imported
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from llm_search import LLMSearchEngine, enhance_existing_search_with_llm
    LLM_AVAILABLE = True
    logger.info("LLM search capabilities loaded successfully")
except ImportError as e:
    LLM_AVAILABLE = False
    logger.warning(f"LLM search capabilities not available: {e}. Install openai, tiktoken, and sklearn to enable.")

def clean_and_normalize_text(text: str) -> str:
    """
    Clean and normalize text for better phrase matching.
    Handles PDF extraction artifacts, OCR issues, and formatting inconsistencies.
    """
    if not text:
        return ""
    
    # Normalize Unicode characters (handle encoding issues)
    text = unicodedata.normalize('NFKD', text)
    
    # Remove soft hyphens and other invisible characters
    text = text.replace('\u00ad', '')  # soft hyphen
    text = text.replace('\u200b', '')  # zero-width space
    text = text.replace('\u200c', '')  # zero-width non-joiner
    text = text.replace('\u200d', '')  # zero-width joiner
    text = text.replace('\ufeff', '')  # byte order mark
    text = text.replace('\u00a0', ' ')  # non-breaking space
    
    # Handle line breaks and formatting
    text = text.replace('\r\n', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    
    # Handle PDF-specific formatting issues
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)  # Remove line-break hyphens
    text = re.sub(r'(\w)\s*\n\s*(\w)', r'\1 \2', text)  # Join words split across lines
    
    # Collapse multiple spaces into single spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove extra spaces around punctuation
    text = re.sub(r'\s+([.!?,:;])', r'\1', text)
    text = re.sub(r'([.!?,:;])\s+', r'\1 ', text)
    
    return text.strip()

def create_flexible_phrase_pattern(phrase: str) -> str:
    """
    Create a flexible regex pattern for phrase matching that handles:
    - Hyphens vs spaces (e.g., "body-clearance" vs "body clearance")
    - Extra whitespace and invisible characters
    - Case insensitivity
    - Word boundaries
    """
    # Escape special regex characters but preserve spaces and hyphens
    words = phrase.strip().split()
    escaped_words = [re.escape(word) for word in words]
    
    # Join words with very flexible separator that handles:
    # - Multiple spaces, tabs, newlines
    # - Hyphens with or without spaces
    # - Invisible Unicode characters
    flexible_separator = r'[\s\-\u00ad\u200b\u200c\u200d\u00a0]*'
    
    # Create pattern with word boundaries
    pattern = r'\b' + flexible_separator.join(escaped_words) + r'\b'
    
    return pattern

app = Flask(__name__)
CORS(app)

# Configuration
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'documents')
LOCALES_DIR = os.path.join(os.path.dirname(__file__), '..', 'locales')

# Document index storage
document_index = {}
translation_map = {}

def load_translation_map():
    """Load French to English translation/synonym map"""
    global translation_map
    translation_map = {
        # Environmental terms
        "évaluation environnementale": ["environmental assessment", "environmental evaluation"],
        "impact environnemental": ["environmental impact"],
        "développement durable": ["sustainable development"],
        "protection": ["protection"],
        "qualité": ["quality"],
        "sécurité": ["security", "safety"],
        "conformité": ["compliance"],
        "réglementation": ["regulation", "regulatory"],
        "norme": ["standard", "norm"],
        "procédure": ["procedure", "process"],
        "méthode": ["method", "methodology"],
        "analyse": ["analysis", "analyze"],
        "test": ["test", "testing"],
        "mesure": ["measurement", "measure"],
        "contrôle": ["control", "inspection"],
        "surveillance": ["monitoring", "surveillance"],
        "documentation": ["documentation"],
        "rapport": ["report"],
        "guide": ["guide", "guidance"],
        "manuel": ["manual"],
        "spécification": ["specification"],
        "exigence": ["requirement"],
        "critère": ["criteria", "criterion"],
        "performance": ["performance"],
        "efficacité": ["efficiency", "effectiveness"],
        "gestion": ["management"],
        "système": ["system"],
        "processus": ["process"],
        "opération": ["operation"],
        "maintenance": ["maintenance"],
        "inspection": ["inspection"],
        "vérification": ["verification"],
        "validation": ["validation"],
        "certification": ["certification"],
        "audit": ["audit"],
        "risque": ["risk"],
        "danger": ["hazard", "danger"],
        "prévention": ["prevention"],
        "formation": ["training"],
        "compétence": ["competence", "skill"],
        "personnel": ["personnel", "staff"],
        "équipement": ["equipment"],
        "matériel": ["material", "equipment"],
        "outil": ["tool"],
        "instrument": ["instrument"],
        "technologie": ["technology"],
        "innovation": ["innovation"],
        "recherche": ["research"],
        "développement": ["development"],
        "amélioration": ["improvement"]
    }

def extract_text_from_pdf(file_path: str) -> Dict[str, Any]:
    """Extract text from PDF with section detection and OCR fallback"""
    try:
        extracted_data = {
            'title': os.path.basename(file_path),
            'sections': [],
            'full_text': ''
        }
        
        # Try with pdfplumber first
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    # Clean and normalize the page text
                    page_text = clean_and_normalize_text(page_text)
                    
                    # Create a section for each page
                    page_section = {
                        'title': f'Page {page_num + 1}',
                        'number': str(page_num + 1),
                        'content': [page_text],
                        'page': page_num + 1
                    }
                    extracted_data['sections'].append(page_section)
                    extracted_data['full_text'] += page_text + '\n'
                else:
                    # Try OCR for this page
                    try:
                        # Convert page to image and apply OCR
                        page_image = page.to_image(resolution=150)
                        pil_image = page_image.original
                        ocr_text = pytesseract.image_to_string(pil_image)
                        if ocr_text.strip():
                            # Clean and normalize OCR text
                            ocr_text = clean_and_normalize_text(ocr_text)
                            
                            # Create a page-specific OCR section
                            ocr_section = {
                                'title': f'Page {page_num + 1} (OCR)',
                                'number': str(page_num + 1),
                                'content': [ocr_text],
                                'page': page_num + 1
                            }
                            extracted_data['sections'].append(ocr_section)
                            extracted_data['full_text'] += ocr_text + '\n'
                    except Exception as ocr_error:
                        logger.warning(f"OCR failed for page {page_num + 1}: {ocr_error}")
        
        # If no text was extracted, try PyMuPDF with OCR
        if not extracted_data['full_text'].strip():
            extracted_data = extract_with_pymupdf_ocr(file_path)
        
        return extracted_data
        
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return {
            'title': os.path.basename(file_path),
            'sections': [],
            'full_text': '',
            'error': str(e)
        }

def extract_with_pymupdf_ocr(file_path: str) -> Dict[str, Any]:
    """Fallback OCR extraction using PyMuPDF"""
    try:
        doc = fitz.open(file_path)
        extracted_data = {
            'title': os.path.basename(file_path),
            'sections': [],
            'full_text': ''        }
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # First try to extract text normally
            text = page.get_text()
            
            if not text.strip():
                # Apply OCR
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                text = pytesseract.image_to_string(image)
            
            if text.strip():
                # Clean and normalize the extracted text
                text = clean_and_normalize_text(text)
                
                section = {
                    'title': f'Page {page_num + 1}',
                    'number': str(page_num + 1),
                    'content': [text],
                    'page': page_num + 1
                }
                extracted_data['sections'].append(section)
                extracted_data['full_text'] += text + '\n'
        
        doc.close()
        return extracted_data
        
    except Exception as e:
        logger.error(f"PyMuPDF OCR failed for {file_path}: {e}")
        return {
            'title': os.path.basename(file_path),
            'sections': [],
            'full_text': '',
            'error': str(e)
        }

def index_documents():
    """Index all PDF documents in the documents directory"""
    global document_index
    
    if not os.path.exists(DOCUMENTS_DIR):
        logger.warning(f"Documents directory not found: {DOCUMENTS_DIR}")
        return
    
    pdf_files = [f for f in os.listdir(DOCUMENTS_DIR) if f.lower().endswith('.pdf')]
    
    for pdf_file in pdf_files:
        file_path = os.path.join(DOCUMENTS_DIR, pdf_file)
        logger.info(f"Indexing document: {pdf_file}")
        
        document_data = extract_text_from_pdf(file_path)
        document_index[pdf_file] = document_data

def parse_search_query(query: str) -> List[Dict[str, Any]]:
    """Parse search query to extract exact phrases and regular terms"""
    terms = []
    
    # Find quoted phrases using regex
    quoted_pattern = r'"([^"]*)"'
    quoted_matches = re.findall(quoted_pattern, query)
    
    # Remove quoted phrases from the query to get remaining terms
    query_without_quotes = re.sub(quoted_pattern, '', query)
    
    # Add exact phrases
    for phrase in quoted_matches:
        phrase = phrase.strip()
        if phrase:
            terms.append({
                'text': phrase,
                'is_exact': True
            })
    
    # Add individual terms (not in quotes)
    individual_terms = [term.strip() for term in query_without_quotes.split() if term.strip()]
    for term in individual_terms:
        terms.append({
            'text': term,
            'is_exact': False
        })
    
    return terms

def translate_search_terms(search_terms: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
    """Translate French search terms to English equivalents"""
    if language != 'fr':
        return search_terms
    
    translated_terms = []
    
    for term_obj in search_terms:
        term = term_obj['text']
        is_exact = term_obj['is_exact']
        
        if is_exact:
            # For exact phrases, only translate the whole phrase if found
            term_lower = term.lower().strip()
            
            # Check for exact phrase matches in translation map
            if term_lower in translation_map:
                for english_equiv in translation_map[term_lower]:
                    translated_terms.append({
                        'text': english_equiv,
                        'is_exact': True
                    })
            
            # Always include the original exact phrase
            translated_terms.append(term_obj)
        else:
            # For individual terms, use existing logic
            term_lower = term.lower().strip()
            
            # Check for exact matches in translation map
            if term_lower in translation_map:
                for english_equiv in translation_map[term_lower]:
                    translated_terms.append({
                        'text': english_equiv,
                        'is_exact': False
                    })
            
            # Check for partial matches
            for french_term, english_terms in translation_map.items():
                if term_lower in french_term or french_term in term_lower:
                    for english_equiv in english_terms:
                        translated_terms.append({
                            'text': english_equiv,
                            'is_exact': False
                        })
            
            # Always include the original term
            translated_terms.append(term_obj)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_terms = []
    for term_obj in translated_terms:
        key = (term_obj['text'].lower(), term_obj['is_exact'])
        if key not in seen:
            seen.add(key)
            unique_terms.append(term_obj)
    
    return unique_terms

def search_in_text(text: str, search_terms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Search for terms in text and return matches with context.
    Uses improved text normalization and flexible phrase matching.
    """
    matches = []
    
    # Clean and normalize the entire text first
    cleaned_text = clean_and_normalize_text(text)
    if not cleaned_text:
        return matches
    
    # Split into sentences for context, but search in larger blocks
    sentences = re.split(r'[.!?]+', text)  # Use original text for context
    cleaned_sentences = [clean_and_normalize_text(s) for s in sentences]
    
    # Also create larger search blocks (paragraphs) for better phrase detection
    paragraphs = re.split(r'\n\s*\n', text)
    cleaned_paragraphs = [clean_and_normalize_text(p) for p in paragraphs]
    
    for term_obj in search_terms:
        term = term_obj['text']
        is_exact = term_obj['is_exact']
        term_normalized = clean_and_normalize_text(term).lower()
        
        if is_exact:
            # For exact phrases, use more precise matching
            pattern = create_flexible_phrase_pattern(term_normalized)
            found_exact_match = False
            
            # First try: exact regex pattern in paragraphs (best for phrases)
            for para_idx, cleaned_para in enumerate(cleaned_paragraphs):
                if not cleaned_para:
                    continue
                    
                if re.search(pattern, cleaned_para.lower(), re.IGNORECASE):
                    # Find the best sentence context within this paragraph
                    para_sentences = re.split(r'[.!?]+', paragraphs[para_idx])
                    
                    for sent_idx, sentence in enumerate(para_sentences):
                        cleaned_sent = clean_and_normalize_text(sentence)
                        if cleaned_sent and re.search(pattern, cleaned_sent.lower(), re.IGNORECASE):
                            # Get surrounding context
                            start_idx = max(0, sent_idx - 1)
                            end_idx = min(len(para_sentences), sent_idx + 2)
                            context_sentences = para_sentences[start_idx:end_idx]
                            context = '. '.join(s.strip() for s in context_sentences if s.strip())
                            
                            # Highlight the matched phrase
                            highlighted_context = re.sub(
                                pattern,
                                lambda m: f'<mark>{m.group()}</mark>',
                                context,
                                flags=re.IGNORECASE
                            )
                            
                            matches.append({
                                'matched_term': term + ' (exact phrase)',
                                'context': context,
                                'highlighted_context': highlighted_context,
                                'sentence_index': sent_idx,
                                'is_exact': True
                            })
                            found_exact_match = True
                            break  # Only match once per paragraph
                    
                    if found_exact_match:
                        break  # Found in this paragraph, don't search further paragraphs for this term
              # Second try: if no exact match found, try a more precise proximity approach
            if not found_exact_match:
                words = term_normalized.split()
                if len(words) == 2:  # Only for two-word phrases
                    word1, word2 = words
                    
                    # Look for sentences where both words appear as complete words close together
                    for i, cleaned_sentence in enumerate(cleaned_sentences):
                        if not cleaned_sentence:
                            continue
                        
                        sent_lower = cleaned_sentence.lower()
                        
                        # Use word boundaries to ensure we match complete words only
                        word1_pattern = r'\b' + re.escape(word1) + r'\b'
                        word2_pattern = r'\b' + re.escape(word2) + r'\b'
                        
                        word1_match = re.search(word1_pattern, sent_lower)
                        word2_match = re.search(word2_pattern, sent_lower)
                        
                        if word1_match and word2_match:
                            # Check if words are reasonably close (within 20 characters of each other)
                            word1_pos = word1_match.start()
                            word2_pos = word2_match.start()
                            
                            if abs(word1_pos - word2_pos) <= 20:
                                # Get context (current sentence + surrounding sentences)
                                start_idx = max(0, i - 1)
                                end_idx = min(len(sentences), i + 2)
                                context_sentences = sentences[start_idx:end_idx]
                                context = '. '.join(s.strip() for s in context_sentences if s.strip())
                                
                                # Only add if context is meaningful (not just garbled text)
                                if len(context.strip()) > 20 and not re.match(r'^[\s\w]{1,3}$', context.strip()):
                                    # Simple highlighting of both words
                                    highlighted_context = context
                                    for word in words:
                                        highlighted_context = re.sub(
                                            r'\b(' + re.escape(word) + r')\b',
                                            r'<mark>\1</mark>',
                                            highlighted_context,
                                            flags=re.IGNORECASE
                                        )
                                    
                                    matches.append({
                                        'matched_term': term + ' (exact phrase - proximity)',
                                        'context': context,
                                        'highlighted_context': highlighted_context,
                                        'sentence_index': i,
                                        'is_exact': True
                                    })
                                    break  # Only find one proximity match per term
        else:
            # For individual terms, use simpler matching but still normalize
            for i, cleaned_sentence in enumerate(cleaned_sentences):
                if not cleaned_sentence:
                    continue
                    
                if term_normalized in cleaned_sentence.lower():
                    # Get context (current sentence + surrounding sentences)
                    start_idx = max(0, i - 1)
                    end_idx = min(len(sentences), i + 2)
                    context_sentences = sentences[start_idx:end_idx]
                    context = '. '.join(s.strip() for s in context_sentences if s.strip())
                    
                    # Highlight the matched term
                    highlighted_context = re.sub(
                        f'({re.escape(term)})',
                        r'<mark>\1</mark>',
                        context,
                        flags=re.IGNORECASE
                    )
                    
                    matches.append({
                        'matched_term': term,
                        'context': context,
                        'highlighted_context': highlighted_context,
                        'sentence_index': i,
                        'is_exact': False
                    })
    
    return matches

def search_in_text_enhanced(text: str, search_terms: List[Dict[str, Any]], debug_mode: bool = False) -> List[Dict[str, Any]]:
    """
    Enhanced search function with more aggressive text cleaning and multiple search strategies.
    """
    matches = []
    
    if not text or not search_terms:
        return matches
    
    # Multiple levels of text cleaning for robustness
    original_text = text
    cleaned_text = clean_and_normalize_text(text)
    
    # Also try with more aggressive cleaning
    aggressive_clean = re.sub(r'[^\w\s]', ' ', cleaned_text.lower())
    aggressive_clean = re.sub(r'\s+', ' ', aggressive_clean).strip()
    
    if debug_mode:
        logger.info(f"Original text length: {len(original_text)}")
        logger.info(f"Cleaned text length: {len(cleaned_text)}")
        logger.info(f"Aggressive clean length: {len(aggressive_clean)}")
    
    # Split into searchable units
    sentences = re.split(r'[.!?]+', original_text)
    cleaned_sentences = [clean_and_normalize_text(s) for s in sentences]
    
    # Also create larger blocks (paragraphs) for phrase detection
    paragraphs = re.split(r'\n\s*\n', original_text)
    cleaned_paragraphs = [clean_and_normalize_text(p) for p in paragraphs]
    
    for term_obj in search_terms:
        term = term_obj['text']
        is_exact = term_obj['is_exact']
        term_normalized = clean_and_normalize_text(term).lower()
        
        if debug_mode:
            logger.info(f"Searching for: '{term}' (exact: {is_exact})")
            logger.info(f"Normalized: '{term_normalized}'")
        
        if is_exact:
            # Multiple search strategies for exact phrases
            found_matches = []
            
            # Strategy 1: Flexible regex pattern
            pattern = create_flexible_phrase_pattern(term_normalized)
            
            # Search in paragraphs (better for phrases spanning lines)
            for para_idx, paragraph in enumerate(paragraphs):
                cleaned_para = clean_and_normalize_text(paragraph)
                if re.search(pattern, cleaned_para, re.IGNORECASE):
                    found_matches.append(('paragraph', para_idx, paragraph, cleaned_para))
            
            # Strategy 2: Simple substring search with various normalizations
            search_variants = [
                term_normalized,
                term_normalized.replace(' ', ''),  # No spaces
                term_normalized.replace(' ', '-'), # Hyphenated
                term_normalized.replace(' ', '_'), # Underscored
                re.sub(r'\s+', ' ', term_normalized), # Single spaces
            ]
            
            for variant in search_variants:
                if variant in aggressive_clean:
                    # Find the location and extract context
                    start_pos = aggressive_clean.find(variant)
                    if start_pos >= 0:
                        # Map back to original text approximately
                        context_start = max(0, start_pos - 100)
                        context_end = min(len(cleaned_text), start_pos + len(variant) + 100)
                        context = cleaned_text[context_start:context_end]
                        found_matches.append(('variant', variant, context, context))
                        if debug_mode:
                            logger.info(f"Found variant '{variant}' in aggressive clean")
                        break
              # Strategy 3: Word-by-word proximity search with word boundaries
            words = term_normalized.split()
            if len(words) > 1:
                # Look for words that appear close to each other as complete words
                for sent_idx, sentence in enumerate(cleaned_sentences):
                    if not sentence:
                        continue
                    
                    sentence_lower = sentence.lower()
                    word_positions = []
                    
                    for word in words:
                        # Use word boundaries to find complete words only
                        word_pattern = r'\b' + re.escape(word) + r'\b'
                        match = re.search(word_pattern, sentence_lower)
                        if match:
                            word_positions.append((word, match.start()))
                    
                    # If we found all words in the sentence
                    if len(word_positions) >= len(words):
                        # Check if they're reasonably close (within 50 characters of each other)
                        positions = [pos for _, pos in word_positions]
                        if max(positions) - min(positions) <= 50:
                            # Only add if this looks like meaningful content
                            original_sentence = sentences[sent_idx] if sent_idx < len(sentences) else sentence
                            if len(original_sentence.strip()) > 20 and not re.match(r'^[\s\w]{1,5}$', original_sentence.strip()):
                                found_matches.append(('proximity', sent_idx, original_sentence, sentence))
                                if debug_mode:
                                    logger.info(f"Found proximity match in sentence {sent_idx}")
                                break  # Only one proximity match per term
              # Add unique matches to results with quality filtering
            for match_type, idx, original_context, cleaned_context in found_matches:
                # Filter out garbled or very short contexts
                if len(original_context.strip()) < 20:
                    continue
                if re.match(r'^[\s\w]{1,5}$', original_context.strip()):
                    continue
                if len(original_context.strip().split()) < 3:
                    continue
                
                # Create highlighted context
                highlighted_context = original_context
                for word in term.split():
                    highlighted_context = re.sub(
                        r'\b(' + re.escape(word) + r')\b',
                        r'<mark>\1</mark>',
                        highlighted_context,
                        flags=re.IGNORECASE
                    )
                
                matches.append({
                    'matched_term': f"{term} (exact phrase - {match_type})",
                    'context': original_context[:500],  # Limit context length
                    'highlighted_context': highlighted_context[:500],
                    'sentence_index': idx,
                    'is_exact': True,
                    'match_strategy': match_type
                })
                
                if debug_mode:
                    logger.info(f"Added match: {match_type} - {original_context[:100]}...")
        
        else:
            # Individual word search - use existing logic but with enhanced cleaning
            for i, sentence in enumerate(cleaned_sentences):
                if not sentence:
                    continue
                
                if term_normalized in sentence.lower():
                    context = sentences[i] if i < len(sentences) else sentence
                    highlighted_context = re.sub(
                        f'({re.escape(term)})',
                        r'<mark>\1</mark>',
                        context,
                        flags=re.IGNORECASE
                    )
                    
                    matches.append({
                        'matched_term': term,
                        'context': context[:500],
                        'highlighted_context': highlighted_context[:500],
                        'sentence_index': i,
                        'is_exact': False
                    })
    
    if debug_mode:
        logger.info(f"Total matches found: {len(matches)}")
    
    return matches

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of available documents"""
    documents = []
    for filename, data in document_index.items():
        documents.append({
            'filename': filename,
            'title': data['title'],
            'sections_count': len(data['sections'])
        })
    
    return jsonify({'documents': documents})

@app.route('/api/search', methods=['POST'])
def search_documents():
    """Search across selected documents"""
    try:
        data = request.get_json()
        search_query = data.get('query', '').strip()
        selected_documents = data.get('documents', [])
        language = data.get('language', 'en')
        
        if not search_query:
            return jsonify({'error': 'Search query is required'}), 400
          # Parse search terms - handle quoted phrases
        search_terms = parse_search_query(search_query)
        
        # Translate terms if needed
        translated_terms = translate_search_terms(search_terms, language)
        
        results = []
        
        # Search in selected documents (or all if none selected)
        documents_to_search = selected_documents if selected_documents else list(document_index.keys())
        
        for doc_filename in documents_to_search:
            if doc_filename not in document_index:
                continue
                
            doc_data = document_index[doc_filename]
            doc_results = []            # Search in each section
            for section in doc_data['sections']:
                section_content = '\n'.join(section['content'])
                matches = search_in_text(section_content, translated_terms)
                
                # If no exact phrase matches found, try enhanced search for exact phrases
                exact_phrase_terms = [term for term in translated_terms if term.get('is_exact', False)]
                if not matches and exact_phrase_terms:
                    logger.info(f"No matches found with regular search, trying enhanced search for {doc_filename}")
                    matches = search_in_text_enhanced(section_content, exact_phrase_terms, debug_mode=False)
                
                for match in matches:
                    doc_results.append({
                        'document': doc_data['title'],
                        'filename': doc_filename,
                        'section_title': section['title'],
                        'section_number': section['number'],
                        'page': section['page'],
                        'matched_term': match['matched_term'],
                        'context': match['context'],
                        'highlighted_context': match['highlighted_context']
                    })
            
            results.extend(doc_results)
          # Sort results by relevance (document name, then section number)
        results.sort(key=lambda x: (x['document'], int(x['section_number']) if x['section_number'].isdigit() else 999))
        
        # Optional LLM enhancement
        llm_response = None
        if LLM_AVAILABLE and data.get('use_llm', False) and results:
            try:
                llm_engine = LLMSearchEngine()
                enhancement = enhance_existing_search_with_llm(search_query, results, llm_engine)
                llm_response = enhancement
            except Exception as llm_error:
                logger.warning(f"LLM enhancement failed: {llm_error}")
        
        response_data = {
            'results': results,
            'search_terms': [term['text'] for term in search_terms],
            'translated_terms': [term['text'] for term in translated_terms],
            'total_matches': len(results)
        }
        
        if llm_response:
            response_data['llm_enhanced'] = llm_response
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'documents_indexed': len(document_index)
    })

@app.route('/api/debug/document/<document_name>', methods=['GET'])
def debug_document(document_name):
    """Debug endpoint to examine document extraction"""
    try:
        if document_name not in document_index:
            return jsonify({'error': 'Document not found'}), 404
        
        doc_data = document_index[document_name]
        search_term = request.args.get('search', '').lower()
        
        debug_info = {
            'document': document_name,
            'total_sections': len(doc_data['sections']),
            'full_text_length': len(doc_data['full_text']),
            'sections': []
        }
        
        # Look for sections containing the search term
        for i, section in enumerate(doc_data['sections']):
            section_text = ' '.join(section['content']).lower()
            
            section_info = {
                'index': i,
                'title': section['title'],
                'number': section['number'],
                'page': section.get('page', 'Unknown'),
                'content_length': len(section_text),
                'contains_search': search_term in section_text if search_term else False
            }
            
            # If search term provided and found in this section
            if search_term and search_term in section_text:
                # Find context around the search term
                import re
                sentences = re.split(r'[.!?]+', ' '.join(section['content']))
                matching_sentences = []
                
                for sentence in sentences:
                    if search_term in sentence.lower():
                        matching_sentences.append(sentence.strip())
                
                section_info['matching_sentences'] = matching_sentences[:5]  # Limit to 5
                section_info['first_100_chars'] = section_text[:100]
            
            debug_info['sections'].append(section_info)
        
        # Search full text for the term
        if search_term:
            full_text_lower = doc_data['full_text'].lower()
            debug_info['search_term'] = search_term
            debug_info['found_in_full_text'] = search_term in full_text_lower
            
            # Find all occurrences with context
            if search_term in full_text_lower:
                import re
                pattern = f'.{{0,50}}{re.escape(search_term)}.{{0,50}}'
                matches = re.findall(pattern, full_text_lower, re.IGNORECASE)
                debug_info['matches_with_context'] = matches[:10]  # Limit to 10
        
        return jsonify(debug_info)
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/search', methods=['POST'])
def debug_search():
    """Debug endpoint for troubleshooting search issues"""
    try:
        data = request.get_json()
        search_query = data.get('query', '').strip()
        document_name = data.get('document', '')
        
        if not search_query:
            return jsonify({'error': 'Search query is required'}), 400
            
        if document_name and document_name not in document_index:
            return jsonify({'error': 'Document not found'}), 404
        
        # Parse search terms
        search_terms = parse_search_query(search_query)
        
        debug_results = {
            'query': search_query,
            'parsed_terms': search_terms,
            'document_results': {}
        }
        
        # Search in specified document or all documents
        docs_to_search = [document_name] if document_name else list(document_index.keys())
        
        for doc_name in docs_to_search:
            doc_data = document_index[doc_name]
            doc_debug = {
                'total_sections': len(doc_data['sections']),
                'full_text_length': len(doc_data['full_text']),
                'section_results': []
            }
            
            # Search each section with debug mode enabled
            for section_idx, section in enumerate(doc_data['sections']):
                section_text = ' '.join(section['content'])
                
                # Use enhanced search with debug mode
                matches = search_in_text_enhanced(section_text, search_terms, debug_mode=True)
                
                section_debug = {
                    'section_index': section_idx,
                    'section_title': section['title'],
                    'section_number': section['number'],
                    'page': section.get('page', 'Unknown'),
                    'content_length': len(section_text),
                    'matches_found': len(matches),
                    'matches': matches[:3]  # Limit to first 3 matches per section
                }
                
                # Also check if individual words are present
                for term_obj in search_terms:
                    term = term_obj['text'].lower()
                    words = term.split()
                    word_presence = {}
                    for word in words:
                        word_presence[word] = word in section_text.lower()
                    section_debug[f'word_presence_{term}'] = word_presence
                
                if matches or any(term_obj['text'].lower() in section_text.lower() for term_obj in search_terms):
                    doc_debug['section_results'].append(section_debug)
            
            debug_results['document_results'][doc_name] = doc_debug
        
        return jsonify(debug_results)
        
    except Exception as e:
        logger.error(f"Debug search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/llm/chat', methods=['POST'])
def llm_chat():
    """LLM-powered chat interface for document queries"""
    if not LLM_AVAILABLE:
        return jsonify({'error': 'LLM capabilities not available. Install required packages.'}), 503
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        selected_documents = data.get('documents', [])
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Initialize LLM engine
        llm_engine = LLMSearchEngine()
        
        # Perform hybrid search (semantic + LLM)
        results = llm_engine.hybrid_search(
            query, 
            document_index, 
            use_semantic=True, 
            use_llm=True,
            top_k=5
        )
        
        return jsonify({
            'query': query,
            'llm_response': results['llm_response'],
            'semantic_matches': results['semantic_matches'],
            'related_sections': results['combined_results'],
            'tokens_used': results.get('tokens_used', 0)
        })
        
    except Exception as e:
        logger.error(f"LLM chat error: {e}")
        return jsonify({'error': f'LLM chat failed: {str(e)}'}), 500

@app.route('/api/llm/status', methods=['GET'])
def llm_status():
    """Check LLM availability and configuration"""
    status = {
        'llm_available': LLM_AVAILABLE,
        'openai_api_key_configured': bool(os.getenv('OPENAI_API_KEY'))
    }
    
    if LLM_AVAILABLE:
        try:
            llm_engine = LLMSearchEngine()
            status['llm_engine_ready'] = True
            status['embedding_model'] = llm_engine.embedding_model
            status['chat_model'] = llm_engine.model
        except Exception as e:
            status['llm_engine_ready'] = False
            status['error'] = str(e)
    
    return jsonify(status)

@app.route('/api/llm/index', methods=['POST'])
def create_llm_index():
    """Create semantic embeddings for all documents"""
    if not LLM_AVAILABLE:
        return jsonify({'error': 'LLM capabilities not available'}), 503
    
    try:
        llm_engine = LLMSearchEngine()
        llm_engine.index_documents_with_embeddings(document_index)
        
        return jsonify({
            'status': 'success',
            'embeddings_created': len(llm_engine.section_embeddings),
            'documents_processed': len(document_index)
        })
        
    except Exception as e:
        logger.error(f"LLM indexing error: {e}")
        return jsonify({'error': f'Indexing failed: {str(e)}'}), 500

@app.route('/api/documents/<document_name>/preview', methods=['GET'])
def get_document_preview(document_name):
    """Get PDF preview for a specific page with optional text highlighting"""
    try:
        # Check if document exists
        if document_name not in document_index:
            return jsonify({'error': 'Document not found'}), 404
        
        page_number = request.args.get('page', 1, type=int)
        search_terms = request.args.get('search', '', type=str)
        
        # Construct file path
        file_path = os.path.join(DOCUMENTS_DIR, document_name)
        if not os.path.exists(file_path):
            return jsonify({'error': 'PDF file not found'}), 404
        
        # Use PyMuPDF to render PDF page as image
        try:
            doc = fitz.open(file_path)
            if page_number < 1 or page_number > len(doc):
                return jsonify({'error': 'Page number out of range'}), 400
            
            page = doc.load_page(page_number - 1)  # 0-indexed
            
            # Highlight search terms if provided
            if search_terms:
                highlight_search_terms_in_page(page, search_terms)
            
            # Render page to image with higher quality
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x zoom for better quality
            img_data = pix.tobytes("png")
            
            doc.close()
            
            # Return image as response
            from flask import Response
            return Response(img_data, mimetype='image/png')
            
        except Exception as e:
            logger.error(f"Error rendering PDF page: {e}")
            return jsonify({'error': f'Failed to render page: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"PDF preview error: {e}")
        return jsonify({'error': str(e)}), 500

def highlight_search_terms_in_page(page, search_terms):
    """Highlight search terms in a PDF page using PyMuPDF"""
    try:
        # Parse search terms (handle quoted phrases and individual words)
        terms_to_highlight = []
        
        if search_terms:
            # Split search terms by spaces but preserve quoted phrases
            import shlex
            try:
                parsed_terms = shlex.split(search_terms)
            except ValueError:
                # Fallback if shlex fails (unmatched quotes)
                parsed_terms = search_terms.split()
            
            for term in parsed_terms:
                if term.strip():
                    terms_to_highlight.append(term.strip())
        
        # Highlight each term with a different color
        colors = [
            fitz.utils.getColor("yellow"),      # Primary highlight - yellow
            fitz.utils.getColor("lightgreen"),  # Secondary highlight - light green
            fitz.utils.getColor("lightblue"),   # Tertiary highlight - light blue
            fitz.utils.getColor("pink"),        # Additional highlight - pink
            fitz.utils.getColor("orange"),      # Additional highlight - orange
        ]
        
        total_highlights = 0
        
        for i, term in enumerate(terms_to_highlight[:5]):  # Limit to 5 terms to avoid clutter
            color = colors[i % len(colors)]
            
            # Search for the term in the page (case insensitive)
            text_instances = page.search_for(term, flags=fitz.TEXT_DEHYPHENATE)
            
            # Also try variations of the term for better matching
            if not text_instances and len(term) > 3:
                # Try without common suffixes/prefixes
                variations = [
                    term.lower(),
                    term.upper(),
                    term.capitalize(),
                ]
                
                for variation in variations:
                    text_instances = page.search_for(variation, flags=fitz.TEXT_DEHYPHENATE)
                    if text_instances:
                        break
            
            # Highlight each occurrence
            for inst in text_instances:
                try:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors({"stroke": color, "fill": color})
                    highlight.set_opacity(0.6)  # Make it visible but not too bright
                    highlight.update()
                    total_highlights += 1
                except Exception as e:
                    logger.warning(f"Failed to add highlight annotation: {e}")
                    continue
        
        logger.info(f"Successfully added {total_highlights} highlights for {len(terms_to_highlight)} search terms on page")
        
    except Exception as e:
        logger.warning(f"Failed to highlight search terms: {e}")
        # Don't fail the entire request if highlighting fails

@app.route('/api/documents/<document_name>/info', methods=['GET'])
def get_document_info(document_name):
    """Get document information including page count"""
    try:
        if document_name not in document_index:
            return jsonify({'error': 'Document not found'}), 404
        
        file_path = os.path.join(DOCUMENTS_DIR, document_name)
        if not os.path.exists(file_path):
            return jsonify({'error': 'PDF file not found'}), 404
        
        # Get page count using PyMuPDF
        doc = fitz.open(file_path)
        page_count = len(doc)
        doc.close()
        
        doc_data = document_index[document_name]
        
        return jsonify({
            'filename': document_name,
            'title': doc_data['title'],
            'page_count': page_count,
            'sections_count': len(doc_data['sections'])
        })
        
    except Exception as e:
        logger.error(f"Document info error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load translation map and index documents on startup
    load_translation_map()
    index_documents()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
