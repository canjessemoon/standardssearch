<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Bilingual Document Search Tool

This is a bilingual document search application with a React TypeScript frontend and Python Flask backend.

## Project Structure

- **Frontend**: React with TypeScript, Vite build system, i18n for English/French support
- **Backend**: Python Flask API with PDF processing, OCR, and search capabilities
- **Documents**: 5 fixed English PDF documents for searching
- **Languages**: Interface supports English and French, searches English documents

## Key Technologies

- **Frontend**: React, TypeScript, Vite, react-i18next, axios
- **Backend**: Flask, PDFPlumber, PyMuPDF, Tesseract OCR, spaCy
- **Search**: Keyword matching with French-to-English translation mapping
- **OCR**: Tesseract for image-based PDF content

## Development Guidelines

1. **Internationalization**: All UI strings should use react-i18next with keys in both en.json and fr.json
2. **API Integration**: Use the documentsApi service for all backend communication
3. **Error Handling**: Implement proper error boundaries and user-friendly error messages
4. **Responsive Design**: Ensure mobile-friendly layouts with CSS Grid/Flexbox
5. **Accessibility**: Include proper ARIA labels and keyboard navigation

## Code Style

- Use TypeScript interfaces for all data structures
- Follow React functional components with hooks
- Use CSS-in-JS or CSS modules for styling
- Implement proper loading states and error handling
- Use semantic HTML elements

## Backend Notes

- Documents are automatically indexed on startup
- OCR is applied as fallback for image-based PDFs
- French search terms are translated to English using a predefined mapping
- Results include highlighted context and section information
