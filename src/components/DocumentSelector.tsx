import React from 'react';
import { useTranslation } from 'react-i18next';
import type { Document } from '../services/api';

interface DocumentSelectorProps {
  documents: Document[];
  selectedDocuments: string[];
  onSelectionChange: (selectedDocs: string[]) => void;
}

const DocumentSelector: React.FC<DocumentSelectorProps> = ({
  documents,
  selectedDocuments,
  onSelectionChange,
}) => {
  const { t } = useTranslation();

  const handleSelectAll = () => {
    onSelectionChange(documents.map(doc => doc.filename));
  };

  const handleDeselectAll = () => {
    onSelectionChange([]);
  };

  const handleDocumentToggle = (filename: string) => {
    const isSelected = selectedDocuments.includes(filename);
    if (isSelected) {
      onSelectionChange(selectedDocuments.filter(doc => doc !== filename));
    } else {
      onSelectionChange([...selectedDocuments, filename]);
    }
  };

  return (
    <div className="document-selector">
      <div className="document-selector-header">
        <h3>{t('documents.title')}</h3>
        <div className="document-selector-actions">
          <button
            onClick={handleSelectAll}
            className="selector-button"
            disabled={selectedDocuments.length === documents.length}
          >
            {t('documents.selectAll')}
          </button>
          <button
            onClick={handleDeselectAll}
            className="selector-button"
            disabled={selectedDocuments.length === 0}
          >
            {t('documents.deselectAll')}
          </button>
        </div>
      </div>
      
      <div className="document-list">
        {documents.map((document) => (
          <label key={document.filename} className="document-item">
            <input
              type="checkbox"
              checked={selectedDocuments.includes(document.filename)}
              onChange={() => handleDocumentToggle(document.filename)}
              className="document-checkbox"
            />
            <div className="document-info">
              <span className="document-title">{document.title}</span>
              <span className="document-sections">
                {document.sections_count} sections
              </span>
            </div>
          </label>
        ))}
      </div>
      
      <div className="document-selector-summary">
        {t('documents.selected', { count: selectedDocuments.length })}
      </div>
    </div>
  );
};

export default DocumentSelector;
