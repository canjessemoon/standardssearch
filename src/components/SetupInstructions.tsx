import React from 'react';
import { useTranslation } from 'react-i18next';

const SetupInstructions: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="setup-instructions">
      <h2>🚀 Setup Required</h2>
      <div className="instructions-content">
        <h3>Backend Server Setup</h3>
        <p>The Python Flask backend needs to be running to search your documents.</p>
        
        <div className="setup-steps">
          <h4>📋 Setup Steps:</h4>
          <ol>
            <li>
              <strong>Install Python 3.8+</strong>
              <br />
              Download from <a href="https://python.org" target="_blank" rel="noopener noreferrer">python.org</a>
              <br />
              <em>Make sure to check "Add Python to PATH" during installation</em>
            </li>
            
            <li>
              <strong>Install Backend Dependencies</strong>
              <pre><code>cd backend{'\n'}pip install -r requirements.txt</code></pre>
            </li>
            
            <li>
              <strong>Start the Backend Server</strong>
              <pre><code>python app/main.py</code></pre>
              <p><em>The server will start at http://localhost:5000</em></p>
            </li>
            
            <li>
              <strong>Refresh this page</strong>
              <br />
              Once the backend is running, refresh this page to start searching!
            </li>
          </ol>
        </div>

        <div className="documents-info">
          <h4>📄 Your Documents</h4>
          <p>The following documents are ready to be indexed:</p>
          <ul>
            <li>MIL-HDBK-759B.pdf</li>
            <li>MIL-STD-1472H.pdf</li>
            <li>MIL-STD-1474D.pdf</li>
            <li>MIL-STD-882E.pdf</li>
            <li>NASA-STD-3000B_VOL-1.pdf</li>
          </ul>
        </div>

        <div className="features-info">
          <h4>✨ Features</h4>
          <ul>
            <li>🔍 Search across all 5 documents simultaneously</li>
            <li>🌐 Bilingual interface (English/French)</li>
            <li>🔄 French-to-English search term translation</li>
            <li>📖 OCR support for image-based PDFs</li>
            <li>📍 Contextual results with section information</li>
            <li>🎯 Document selection and filtering</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SetupInstructions;
