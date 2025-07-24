import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { SearchResult } from '../services/api';

interface ResultsViewerProps {
  results: SearchResult[];
  searchQuery: string;
}

const ResultsViewer: React.FC<ResultsViewerProps> = ({ results, searchQuery }) => {
  const { t } = useTranslation();
  const [sortBy, setSortBy] = useState<'document' | 'relevance' | 'section'>('document');
  const [filterByDocument, setFilterByDocument] = useState<string>('');

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
          <div key={index} className="result-item">
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
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsViewer;
