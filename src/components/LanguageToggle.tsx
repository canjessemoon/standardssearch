import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageToggle: React.FC = () => {
  const { i18n, t } = useTranslation();

  const toggleLanguage = () => {
    const newLanguage = i18n.language === 'en' ? 'fr' : 'en';
    i18n.changeLanguage(newLanguage);
  };

  return (
    <div className="language-toggle">
      <button 
        onClick={toggleLanguage}
        className="language-button"
        title={t('language.toggle')}
      >
        <span className="language-label">{t('language.toggle')}:</span>
        <span className="language-current">
          {i18n.language === 'en' ? t('language.english') : t('language.french')}
        </span>
        <span className="language-switch">
          {i18n.language === 'en' ? 'FR' : 'EN'}
        </span>
      </button>
    </div>
  );
};

export default LanguageToggle;
