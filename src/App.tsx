import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './App.css';
import { documentsApi } from './services/api';
import type { Document, SearchResult } from './services/api';
import LanguageToggle from './components/LanguageToggle.tsx';
import SearchPanel from './components/SearchPanel.tsx';
import DocumentSelector from './components/DocumentSelector.tsx';
import ResultsViewer from './components/ResultsViewer.tsx';
import LoadingSpinner from './components/LoadingSpinner.tsx';
import SetupInstructions from './components/SetupInstructions.tsx';
import ChatInterface from './components/ChatInterface.tsx';

function App() {
  const { t } = useTranslation();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [backendAvailable, setBackendAvailable] = useState(true);
  const [activeTab, setActiveTab] = useState<'search' | 'chat'>('search');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoadingDocuments(true);
      const response = await documentsApi.getDocuments();
      setDocuments(response.documents);
      setSelectedDocuments(response.documents.map(doc => doc.filename));
      setError(null);
      setBackendAvailable(true);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setBackendAvailable(false);
      if (err instanceof Error && err.message.includes('Network Error')) {
        setError('Backend server is not running. Please start the Python Flask backend first.');
      } else {
        setError(t('errors.documentsLoadFailed'));
      }
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  const handleSearch = async (query: string, language: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setSearchQuery(query);
      
      const response = await documentsApi.search(query, selectedDocuments, language);
      setSearchResults(response.results);
    } catch (err) {
      console.error('Search failed:', err);
      setError(t('errors.searchFailed'));
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentSelectionChange = (selectedDocs: string[]) => {
    setSelectedDocuments(selectedDocs);
  };

  const clearResults = () => {
    setSearchResults([]);
    setSearchQuery('');
    setError(null);
  };

  if (isLoadingDocuments) {
    return (
      <div className="app loading-container">
        <LoadingSpinner />
        <p>Loading documents...</p>
      </div>
    );
  }

  // Show setup instructions if backend is not available
  if (!backendAvailable) {
    return (
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <h1>{t('app.title')}</h1>
            <p className="subtitle">{t('app.subtitle')}</p>
            <LanguageToggle />
          </div>
        </header>
        <main className="app-main">
          <SetupInstructions />
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>{t('app.title')}</h1>
          <p className="subtitle">{t('app.subtitle')}</p>
          <LanguageToggle />
        </div>
      </header>

      <main className="app-main">
        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            🔍 {t('search.title', 'Keyword Search')}
          </button>
          <button 
            className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            🤖 {t('chat.title', 'AI Assistant')}
          </button>
        </div>

        {activeTab === 'search' ? (
          <>
            <div className="search-section">
              <SearchPanel 
                onSearch={handleSearch}
                onClear={clearResults}
                isLoading={isLoading}
              />
              
              <DocumentSelector
                documents={documents}
                selectedDocuments={selectedDocuments}
                onSelectionChange={handleDocumentSelectionChange}
              />
            </div>

            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}

            <div className="results-section">
              {isLoading ? (
                <div className="loading-container">
                  <LoadingSpinner />
                  <p>{t('search.loading')}</p>
                </div>
              ) : (
                <ResultsViewer 
                  results={searchResults}
                  searchQuery={searchQuery}
                />
              )}
            </div>
          </>
        ) : (
          <ChatInterface selectedDocuments={selectedDocuments} />
        )}
      </main>
    </div>
  );
}

export default App;
