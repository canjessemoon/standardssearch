# LLM-Enhanced Search Module for Document Search Tool
import os
import json
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI
import tiktoken
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class LLMSearchEngine:
    """LLM-powered semantic search engine for document content"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", embedding_model: str = "text-embedding-ada-002"):
        """
        Initialize LLM search engine
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY environment variable)
            model: GPT model for text generation and analysis
            embedding_model: Model for generating embeddings
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_model = embedding_model
        self.encoding = tiktoken.encoding_for_model(model)
        
        # Cache for embeddings to avoid re-computation
        self.document_embeddings = {}
        self.section_embeddings = {}
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, max_tokens: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into smaller chunks for embedding"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), max_tokens - overlap):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return []
    
    def index_documents_with_embeddings(self, document_index: Dict[str, Any]):
        """Create embeddings for all document sections"""
        logger.info("Creating embeddings for document sections...")
        
        for doc_name, doc_data in document_index.items():
            logger.info(f"Processing embeddings for {doc_name}")
            doc_embeddings = []
            
            for section_idx, section in enumerate(doc_data['sections']):
                section_content = ' '.join(section['content'])
                
                # Skip very short sections
                if len(section_content.strip()) < 50:
                    continue
                
                # Chunk large sections
                chunks = self.chunk_text(section_content, max_tokens=800)
                
                for chunk_idx, chunk in enumerate(chunks):
                    embedding = self.get_embedding(chunk)
                    if embedding:
                        section_key = f"{doc_name}_{section_idx}_{chunk_idx}"
                        self.section_embeddings[section_key] = {
                            'embedding': embedding,
                            'content': chunk,
                            'document': doc_name,
                            'section': section,
                            'section_index': section_idx,
                            'chunk_index': chunk_idx
                        }
        
        logger.info(f"Created embeddings for {len(self.section_embeddings)} document chunks")
    
    def semantic_search(self, query: str, top_k: int = 10, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Perform semantic search using embeddings"""
        if not self.section_embeddings:
            return []
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []
        
        # Calculate similarities
        similarities = []
        for section_key, section_data in self.section_embeddings.items():
            similarity = cosine_similarity(
                [query_embedding], 
                [section_data['embedding']]
            )[0][0]
            
            if similarity >= similarity_threshold:
                similarities.append({
                    'section_key': section_key,
                    'similarity': similarity,
                    'data': section_data
                })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def llm_enhanced_search(self, query: str, document_context: str, max_context_tokens: int = 3000) -> Dict[str, Any]:
        """Use LLM to analyze query and provide intelligent responses"""
        
        # Truncate context if too long
        if self.count_tokens(document_context) > max_context_tokens:
            tokens = self.encoding.encode(document_context)
            truncated_tokens = tokens[:max_context_tokens]
            document_context = self.encoding.decode(truncated_tokens)
        
        system_prompt = """You are an expert assistant helping users find information in technical documents. 

Your task is to:
1. Understand the user's query intent
2. Find relevant information in the provided document context
3. Provide accurate, helpful answers based ONLY on the document content
4. Highlight specific quotes and page references when available
5. If the information isn't in the documents, clearly state that

Document context will be provided after the user query."""

        user_prompt = f"""
User Query: {query}

Document Context:
{document_context}

Please provide a helpful response based on the document content. Include:
- Direct answers to the query
- Relevant quotes from the documents
- Page numbers or section references when available
- If multiple documents contain relevant info, organize by document
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.1  # Lower temperature for more factual responses
            )
            
            return {
                'response': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'model': self.model
            }
        
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return {
                'response': f"Error processing query with LLM: {str(e)}",
                'tokens_used': 0,
                'model': self.model
            }
    
    def hybrid_search(self, query: str, document_index: Dict[str, Any], 
                     use_semantic: bool = True, use_llm: bool = True,
                     top_k: int = 5) -> Dict[str, Any]:
        """
        Combine semantic search with LLM analysis for best results
        """
        results = {
            'query': query,
            'semantic_matches': [],
            'llm_response': '',
            'combined_results': []
        }
        
        # Step 1: Semantic search
        if use_semantic and self.section_embeddings:
            semantic_results = self.semantic_search(query, top_k=top_k)
            results['semantic_matches'] = semantic_results
            
            # Collect context from semantic matches
            semantic_context = ""
            for result in semantic_results[:3]:  # Top 3 matches
                section_data = result['data']
                section = section_data['section']
                semantic_context += f"\n--- {section_data['document']} - {section['title']} (Page {section.get('page', 'Unknown')}) ---\n"
                semantic_context += section_data['content']
                semantic_context += "\n\n"
            
            # Step 2: LLM Analysis
            if use_llm and semantic_context.strip():
                llm_result = self.llm_enhanced_search(query, semantic_context)
                results['llm_response'] = llm_result['response']
                results['tokens_used'] = llm_result.get('tokens_used', 0)
            
            # Step 3: Format combined results
            for result in semantic_results:
                section_data = result['data']
                section = section_data['section']
                
                combined_result = {
                    'document': section_data['document'],
                    'section_title': section['title'],
                    'section_number': section['number'],
                    'page': section.get('page', 'Unknown'),
                    'content': section_data['content'][:500] + "...",
                    'similarity_score': result['similarity'],
                    'match_type': 'semantic'
                }
                results['combined_results'].append(combined_result)
        
        return results

# Example usage and configuration
def create_llm_search_engine():
    """Factory function to create LLM search engine"""
    try:
        return LLMSearchEngine()
    except ValueError as e:
        logger.warning(f"LLM search engine not available: {e}")
        return None

# Integration helpers
def enhance_existing_search_with_llm(query: str, existing_results: List[Dict], 
                                   llm_engine: LLMSearchEngine) -> Dict[str, Any]:
    """Enhance existing keyword search results with LLM analysis"""
    if not existing_results or not llm_engine:
        return {'enhanced_response': 'No results to enhance'}
    
    # Combine context from existing results
    context = ""
    for result in existing_results[:5]:  # Top 5 results
        context += f"\n--- {result['document']} - {result['section_title']} (Page {result.get('page', 'Unknown')}) ---\n"
        context += result.get('context', '')
        context += "\n\n"
    
    # Get LLM analysis
    llm_result = llm_engine.llm_enhanced_search(query, context)
    
    return {
        'enhanced_response': llm_result['response'],
        'original_results_count': len(existing_results),
        'tokens_used': llm_result.get('tokens_used', 0)
    }
