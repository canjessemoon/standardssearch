# Bilingual Document Search Tool

A powerful AI-enhanced web-based document search application that allows professionals to search through technical standards and reference documents in both English and French.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/canjessemoon/standardssearch)

## 🌟 Features

- **🤖 AI-Powered Search**: GPT-3.5-turbo and semantic search with OpenAI embeddings
- **🔍 Dual Search Modes**: Traditional keyword search + intelligent AI assistant
- **🌍 Bilingual Interface**: Full support for English and French UI
- **📄 Advanced PDF Processing**: Extract text from both text-based and image-based PDFs using OCR
- **🧠 Intelligent Translation**: French search terms automatically translated to English
- **💬 Natural Language Queries**: Ask questions in plain English about document contents
- **📍 Contextual Results**: View search results with highlighted keywords and surrounding context
- **📑 Document Selection**: Choose which documents to include in your search
- **🏗️ Section Detection**: Automatically identify document sections and structure
- **📱 Responsive Design**: Modern, mobile-friendly interface

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Tesseract OCR installed on your system
- OpenAI API key (for AI features)

### Document Setup

⚠️ **Important**: Due to file size limitations, PDF documents are not included in this repository.

See [DOCUMENTS.md](DOCUMENTS.md) for detailed instructions on downloading and setting up the required PDF documents.

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Standards-Search
   ```

2. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

4. **Set up documents** (see [DOCUMENTS.md](DOCUMENTS.md))

5. **Configure OpenAI API key:**
   ```bash
   # Set environment variable (Windows)
   $env:OPENAI_API_KEY="your-api-key-here"
   
   # Or create a .env file in the root directory
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

### Running the Application

1. **Start the Python backend:**
   ```bash
   # With API key as environment variable
   $env:OPENAI_API_KEY="your-api-key"
   C:/dev/Standards-Search/.venv/Scripts/python.exe backend/app/main.py
   ```

2. **Start the React frontend:**
   ```bash
   npm run dev
   ```

3. **Open your browser** and navigate to `http://localhost:5173`

## 🎯 Usage

### Keyword Search Tab (🔍)
- Traditional search with exact phrase matching
- Use quotes for exact phrases: `"head clearance"`
- French terms automatically translated to English
- Fast, precise results with context highlighting

### AI Assistant Tab (🤖)
- Ask natural language questions about document contents
- Examples:
  - "What are the safety requirements for head clearance?"
  - "Summarize the key ergonomic guidelines"
  - "Find information about noise limits in military standards"

## 📋 API Endpoints

### Standard Search
- `GET /api/documents` - Get list of available documents
- `POST /api/search` - Search documents with query, language, and document selection
- `GET /api/health` - Health check and indexing status

### AI/LLM Endpoints
- `GET /api/llm/status` - Check LLM availability and configuration
- `POST /api/llm/chat` - AI-powered document queries
- `POST /api/llm/index` - Create semantic embeddings for documents

## 🛠️ Technical Architecture

- **Backend**: Python Flask with PDF processing (PDFPlumber, PyMuPDF, Tesseract OCR)
- **Frontend**: React with TypeScript, Vite build system
- **AI Integration**: OpenAI GPT-3.5-turbo and text-embedding-ada-002
- **Search**: Hybrid keyword + semantic search with French-English translation
- **Internationalization**: react-i18next for bilingual support

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```
