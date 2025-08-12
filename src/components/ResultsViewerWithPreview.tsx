import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { SearchResult } from '../services/api';
import './ResultsViewer.css';

// Function to get API URL - matches the one in api.ts
const getApiUrl = () => {
  // Try multiple ways to access the environment variable
  const envUrl = 
    // Standard Next.js/Vercel way
    (typeof window === 'undefined' ? process.env.NEXT_PUBLIC_API_URL : undefined) ||
    // Client-side access
    (typeof window !== 'undefined' && (window as any).__NEXT_DATA__?.props?.pageProps?.env?.NEXT_PUBLIC_API_URL) ||
    // Vite way (fallback)
    (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) ||
    // Direct process.env access
    (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL);

  if (envUrl) {
    return `${envUrl}/api`;
  }
  
  // Hardcode as last resort since we know the Railway URL
  const isProduction = typeof window !== 'undefined' && window.location.hostname === 'standardssearch.vercel.app';
  if (isProduction) {
    return 'https://standardssearch-production.up.railway.app/api';
  }
  
  return 'http://localhost:5000/api';
};

interface ResultsViewerProps {
  results: SearchResult[];
  searchQuery: string;
}

const ResultsViewer: React.FC<ResultsViewerProps> = ({ results, searchQuery }) => {
  const { t } = useTranslation();
  const [sortBy, setSortBy] = useState<'document' | 'relevance' | 'section'>('document');
  const [filterByDocument, setFilterByDocument] = useState<string>('');
  const [selectedResult, setSelectedResult] = useState<SearchResult | null>(null);
  const [showPdfPreview, setShowPdfPreview] = useState(false);

  // Extract search terms for highlighting (remove quotes and clean up)
  const getSearchTermsForHighlighting = (query: string) => {
    if (!query) return '';
    // Remove quotes and extra spaces, but preserve the essential search terms
    return query.replace(/"/g, '').trim();
  };

  const uniqueDocuments = Array.from(new Set(results.map(r => r.document)));

  const filteredResults = results.filter(result => 
    !filterByDocument || result.document === filterByDocument
  );

  const sortedResults = [...filteredResults].sort((a, b) => {
    switch (sortBy) {
      case 'document':
        return a.document.localeCompare(b.document) || 
               parseInt(a.section_number) - parseInt(b.section_number);
      case 'section':
        return parseInt(a.section_number) - parseInt(b.section_number);
      case 'relevance':
      default:
        return a.document.localeCompare(b.document);
    }
  });

  const handlePreviewDocument = (result: SearchResult) => {
    setSelectedResult(result);
    setShowPdfPreview(true);
  };

  if (!searchQuery) {
    return null;
  }

  if (results.length === 0) {
    return (
      <div className="results-viewer">
        <h2>{t('results.title')}</h2>
        <div className="no-results">
          <p>{t('results.noResults')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="results-viewer">
      <div className="results-container">
        {/* Left Panel - Search Results */}
        <div className={`results-panel ${showPdfPreview ? 'with-preview' : ''}`}>
          <div className="results-header">
            <h2>{t('results.title')}</h2>
            <p className="results-count">
              {t('results.totalMatches', { count: results.length })}
            </p>
          </div>

          <div className="results-controls">
            <div className="sort-controls">
              <label>
                Sort by:
                <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)}>
                  <option value="document">Document</option>
                  <option value="section">Section</option>
                  <option value="relevance">Relevance</option>
                </select>
              </label>
            </div>

            <div className="filter-controls">
              <label>
                Filter by document:
                <select 
                  value={filterByDocument} 
                  onChange={(e) => setFilterByDocument(e.target.value)}
                >
                  <option value="">All documents</option>
                  {uniqueDocuments.map(doc => (
                    <option key={doc} value={doc}>{doc}</option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          <div className="results-list">
            {sortedResults.map((result, index) => (
              <div 
                key={index} 
                className={`result-item ${selectedResult === result ? 'selected' : ''}`}
                onClick={() => setSelectedResult(result)}
              >
                <div className="result-header">
                  <h4 className="result-document">{result.document}</h4>
                  <div className="result-meta">
                    <span className="result-section">
                      {result.section_title} (Section {result.section_number})
                    </span>
                    <span className="result-page">
                      {t('results.page', { number: result.page })}
                    </span>
                  </div>
                </div>
                
                <div className="result-content">
                  <p className="result-context" 
                     dangerouslySetInnerHTML={{ __html: result.highlighted_context }} 
                  />
                  <p className="result-matched-term">
                    {t('results.matchedTerm', { term: result.matched_term })}
                  </p>
                </div>

                <div className="result-actions">
                  <button 
                    className="preview-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePreviewDocument(result);
                    }}
                  >
                    📄 {t('results.viewPdf')}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel - PDF Preview */}
        {showPdfPreview && selectedResult && (
          <div className="pdf-preview-panel">
            <div className="pdf-preview-header">
              <h3>📄 {selectedResult.document}</h3>
              <p>Page {selectedResult.page} - {selectedResult.section_title}</p>
              <button 
                className="close-preview"
                onClick={() => setShowPdfPreview(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="pdf-preview-content">
              {/* PDF page as image with highlighted search terms */}
              <img
                src={`${getApiUrl()}/documents/${selectedResult.document}/preview?page=${selectedResult.page}&search=${encodeURIComponent(getSearchTermsForHighlighting(searchQuery))}`}
                alt={`Page ${selectedResult.page} of ${selectedResult.document}`}
                style={{ 
                  width: '100%', 
                  height: 'auto',
                  maxHeight: '600px',
                  objectFit: 'contain',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                  backgroundColor: 'white'
                }}
                onError={(e) => {
                  console.error('Failed to load PDF preview:', e);
                  (e.target as HTMLImageElement).alt = 'Failed to load PDF preview';
                }}
              />
              
              {/* Search terms legend */}
              {searchQuery && (
                <div style={{ 
                  padding: '0.75rem', 
                  fontSize: '0.875rem', 
                  color: '#374151',
                  backgroundColor: '#f9fafb',
                  borderRadius: '0.375rem',
                  marginTop: '0.5rem',
                  border: '1px solid #e5e7eb'
                }}>
                  <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
                    🔍 Search Terms Highlighted:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {getSearchTermsForHighlighting(searchQuery).split(' ').filter(term => term.length > 0).map((term, index) => {
                      const colors = ['#ffeb3b', '#8bc34a', '#03a9f4', '#e91e63', '#ff9800'];
                      const bgColor = colors[index % colors.length];
                      return (
                        <span 
                          key={index}
                          style={{ 
                            backgroundColor: bgColor, 
                            padding: '0.125rem 0.375rem',
                            borderRadius: '0.25rem',
                            fontSize: '0.75rem',
                            fontWeight: '500',
                            opacity: 0.8
                          }}
                        >
                          {term}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
              
              <div className="pdf-navigation">
                <button 
                  onClick={() => {
                    // Navigate to previous page
                    if (selectedResult.page > 1) {
                      setSelectedResult({
                        ...selectedResult,
                        page: selectedResult.page - 1
                      });
                    }
                  }}
                  disabled={selectedResult.page <= 1}
                >
                  ← Previous Page
                </button>
                
                <span>Page {selectedResult.page}</span>
                
                <button 
                  onClick={() => {
                    // Navigate to next page
                    setSelectedResult({
                      ...selectedResult,
                      page: selectedResult.page + 1
                    });
                  }}
                >
                  Next Page →
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsViewer;
