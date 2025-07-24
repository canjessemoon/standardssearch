import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface SearchPanelProps {
  onSearch: (query: string, language: string) => void;
  onClear: () => void;
  isLoading: boolean;
}

const SearchPanel: React.FC<SearchPanelProps> = ({ onSearch, onClear, isLoading }) => {
  const { t, i18n } = useTranslation();
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim(), i18n.language);
    }
  };

  const handleClear = () => {
    setQuery('');
    onClear();
  };

  return (
    <div className="search-panel">
      <h2>{t('search.title', 'Search')}</h2>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t('search.placeholder')}
            className="search-input"
            disabled={isLoading}
          />          <div className="search-buttons">
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="search-button primary"
            >
              {isLoading ? t('search.loading') : t('search.button')}
            </button>
            <button
              type="button"
              onClick={handleClear}
              disabled={isLoading}
              className="search-button secondary"
            >
              {t('search.clear')}
            </button>
          </div>
          <div className="search-tip">
            <small>{t('search.tip')}</small>
          </div>
        </div>
      </form>
    </div>
  );
};

export default SearchPanel;
