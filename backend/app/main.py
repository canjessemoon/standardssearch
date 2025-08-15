"""
Stable version of the Flask backend with memory optimizations and robust PDF extraction
"""

import os
import sys
import json
import logging
import re
from typing import Dict, List, Any, Optional
from functools import lru_cache
from dataclasses import dataclass, asdict

import psutil
import fitz  # PyMuPDF - more stable than pdfplumber
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "https://*.vercel.app", "https://standards-search.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def log_memory(stage=""):
    """Log current memory usage"""
    try:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"Memory usage {stage}: {memory_mb:.1f} MB")
        return memory_mb
    except Exception as e:
        logger.warning(f"Could not get memory info: {e}")
        return 0

# Global variables - now optimized for minimal memory usage
document_index = {}  # Only metadata: {filename: {title, sections_count, file_path}}
document_cache = {}  # LRU cache will be handled manually, max 2 documents

# French to English translation map for search terms
french_to_english = {
    "ergonomie": ["ergonomics", "human factors", "usability"],
    "sécurité": ["safety", "security"],
    "bruit": ["noise", "sound", "acoustic"],
    "éclairage": ["lighting", "illumination"],
    "contrôle": ["control", "management"],
    "interface": ["interface", "display"],
    "hauteur": ["height", "clearance"],
    "dégagement": ["clearance", "space"],
    "tête": ["head", "cranial"],
    "espace": ["space", "room", "area"],
    "dimension": ["dimension", "size", "measurement"],
    "anthropométrie": ["anthropometry", "body measurements"],
    "poste de travail": ["workstation", "workplace"],
    "cockpit": ["cockpit", "flight deck"],
    "cabine": ["cabin", "compartment"],
    "siège": ["seat", "seating"],
    "panneau": ["panel", "display"],
    "commande": ["control", "command"],
    "vision": ["vision", "sight", "visibility"],
    "champ de vision": ["field of view", "visual field"],
    "température": ["temperature", "thermal"],
    "vibration": ["vibration"],
    "accélération": ["acceleration"],
    "force": ["force", "strength"],
    "charge": ["load", "weight"],
    "fatigue": ["fatigue", "tiredness"],
    "stress": ["stress"],
    "performance": ["performance"],
    "erreur": ["error", "mistake"],
    "alarme": ["alarm", "warning"],
    "signal": ["signal", "indicator"],
    "couleur": ["color", "colour"],
    "forme": ["shape", "form"],
    "taille": ["size"],
    "position": ["position", "location"],
    "mouvement": ["movement", "motion"],
    "geste": ["gesture", "movement"],
    "main": ["hand", "manual"],
    "doigt": ["finger"],
    "pied": ["foot", "pedal"],
    "jambe": ["leg"],
    "bras": ["arm"],
    "épaule": ["shoulder"],
    "dos": ["back", "spine"],
    "cou": ["neck"],
    "posture": ["posture", "position"],
    "confort": ["comfort"],
    "douleur": ["pain", "discomfort"],
    "risque": ["risk", "hazard"],
    "prévention": ["prevention"],
    "norme": ["standard", "norm"],
    "spécification": ["specification", "requirement"],
    "exigence": ["requirement", "demand"],
    "test": ["test", "testing"],
    "mesure": ["measure", "measurement"],
    "évaluation": ["evaluation", "assessment"],
    "analyse": ["analysis"],
    "conception": ["design", "conception"],
    "développement": ["development"],
    "amélioration": ["improvement"],
    "optimisation": ["optimization"],
    "efficacité": ["efficiency", "effectiveness"],
    "productivité": ["productivity"],
    "qualité": ["quality"],
    "fiabilité": ["reliability"],
    "maintenance": ["maintenance"],
    "formation": ["training"],
    "instruction": ["instruction"],
    "procédure": ["procedure"],
    "méthode": ["method"],
    "technique": ["technique"],
    "outil": ["tool"],
    "instrument": ["instrument"],
    "technologie": ["technology"],
    "innovation": ["innovation"],
    "recherche": ["research"]
}

@dataclass
class DocumentSection:
    title: str
    content: str
    page: int

@dataclass 
class DocumentData:
    title: str
    sections: List[DocumentSection]
    full_text: str

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\-.,;:()!?"\'/]', ' ', text)
    
    return text.strip()

@lru_cache(maxsize=2)  # Only cache 2 documents at a time to save memory
def get_document_data(file_path: str) -> Optional[DocumentData]:
    """Load document data on-demand with caching"""
    try:
        logger.info(f"Loading document data for: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        # Extract text using stable PyMuPDF
        doc = fitz.open(file_path)
        sections = []
        full_text = ""
        
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                page_text = page.get_text()
                
                if page_text.strip():
                    cleaned_text = clean_text(page_text)
                    if cleaned_text:
                        section = DocumentSection(
                            title=f"Page {page_num + 1}",
                            content=cleaned_text,
                            page=page_num + 1
                        )
                        sections.append(section)
                        full_text += cleaned_text + "\n"
                        
                        if (page_num + 1) % 50 == 0:
                            logger.info(f"Processed {page_num + 1} pages")
                            
            except Exception as e:
                logger.warning(f"Error processing page {page_num + 1}: {e}")
                continue
                
        doc.close()
        
        if not sections:
            logger.warning(f"No text extracted from {file_path}")
            return None
            
        document_data = DocumentData(
            title=os.path.basename(file_path),
            sections=sections,
            full_text=full_text
        )
        
        logger.info(f"Successfully loaded {len(sections)} sections from {file_path}")
        return document_data
        
    except Exception as e:
        logger.error(f"Error loading document {file_path}: {e}")
        return None

def index_documents():
    """Index documents - store only metadata to save memory"""
    global document_index
    
    log_memory("at startup")
    
    documents_dir = os.path.join(os.path.dirname(__file__), "..", "documents")
    
    if not os.path.exists(documents_dir):
        logger.error(f"Documents directory not found: {documents_dir}")
        return
        
    logger.info(f"Looking for documents in: {documents_dir}")
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(documents_dir) if f.lower().endswith('.pdf')]
    logger.info(f"Found PDF files: {pdf_files}")
    
    for filename in pdf_files:
        try:
            file_path = os.path.join(documents_dir, filename)
            logger.info(f"Indexing metadata for: {filename}")
            
            # Quick check to count sections without loading full content
            doc = fitz.open(file_path)
            sections_count = len(doc)  # Number of pages
            doc.close()
            
            # Store only metadata - no content in memory
            document_index[filename] = {
                'title': filename,
                'sections_count': sections_count,
                'file_path': file_path
            }
            
            logger.info(f"Indexed {filename}: {sections_count} sections")
            
        except Exception as e:
            logger.error(f"Error indexing {filename}: {e}")
            continue
    
    log_memory("after indexing metadata")
    logger.info(f"Indexing complete. {len(document_index)} documents indexed.")

def search_documents(query: str, selected_documents: List[str] = None) -> List[Dict]:
    """Search documents with on-demand loading"""
    try:
        log_memory("before search")
        
        if not query.strip():
            return []
            
        query_lower = query.lower()
        results = []
        
        # Translate French terms if needed
        search_terms = set([query_lower])
        for french_term, english_translations in french_to_english.items():
            if french_term in query_lower:
                search_terms.update(english_translations)
        
        # Determine which documents to search
        docs_to_search = selected_documents if selected_documents else list(document_index.keys())
        
        for doc_name in docs_to_search:
            if doc_name not in document_index:
                continue
                
            try:
                # Load document on-demand
                doc_info = document_index[doc_name]
                doc_data = get_document_data(doc_info['file_path'])
                
                if not doc_data:
                    continue
                
                # Search through sections
                for section in doc_data.sections:
                    section_text_lower = section.content.lower()
                    
                    for term in search_terms:
                        if term in section_text_lower:
                            # Find context around the match
                            start_pos = section_text_lower.find(term)
                            context_start = max(0, start_pos - 100)
                            context_end = min(len(section.content), start_pos + len(term) + 100)
                            context = section.content[context_start:context_end]
                            
                            results.append({
                                'document': doc_data.title,
                                'section': section.title,
                                'page': section.page,
                                'context': context,
                                'relevance': 0.8  # Simple relevance score
                            })
                            break  # Only one match per section to avoid duplicates
                            
            except Exception as e:
                logger.error(f"Error searching in {doc_name}: {e}")
                continue
        
        log_memory("after search")
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:50]  # Limit to 50 results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with memory info"""
    memory_mb = log_memory("health check")
    return jsonify({
        'status': 'healthy',
        'memory_mb': memory_mb,
        'documents_indexed': len(document_index),
        'cache_size': len(document_cache)
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of available documents"""
    try:
        documents = []
        for filename, info in document_index.items():
            documents.append({
                'filename': filename,
                'title': info['title'],
                'sections_count': info['sections_count']
            })
        return jsonify(documents)
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return jsonify({'error': 'Failed to retrieve documents'}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Search endpoint"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        selected_documents = data.get('documents', [])
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"Search request: '{query}' in {len(selected_documents) if selected_documents else 'all'} documents")
        
        results = search_documents(query, selected_documents)
        
        return jsonify({
            'results': results,
            'total': len(results),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        return jsonify({'error': 'Search failed'}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Standards Search Backend (Stable Version)")
        log_memory("startup")
        
        # Index documents
        index_documents()
        
        # Start Flask app
        port = int(os.environ.get('PORT', 8080))  # Default to 8080 for Railway
        host = '0.0.0.0'  # Always bind to all interfaces for Railway
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Railway environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
        app.run(host=host, port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
