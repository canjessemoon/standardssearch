import axios from 'axios';

// More robust environment variable detection for Vercel
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

  console.log('Environment check:', {
    processEnv: typeof process !== 'undefined' ? process.env?.NEXT_PUBLIC_API_URL : 'undefined',
    windowUndefined: typeof window === 'undefined',
    envUrl: envUrl
  });

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

const API_BASE_URL = getApiUrl();
console.log('Final API_BASE_URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export interface Document {
  filename: string;
  title: string;
  sections_count: number;
}

export interface SearchResult {
  document: string;
  filename: string;
  section_title: string;
  section_number: string;
  page: number;
  matched_term: string;
  context: string;
  highlighted_context: string;
}

export interface SearchResponse {
  results: SearchResult[];
  search_terms: string[];
  translated_terms: string[];
  total_matches: number;
}

export interface DocumentsResponse {
  documents: Document[];
}

export const documentsApi = {
  getDocuments: async (): Promise<DocumentsResponse> => {
    const response = await api.get<DocumentsResponse>('/documents');
    return response.data;
  },

  search: async (
    query: string,
    documents: string[],
    language: string
  ): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/search', {
      query,
      documents,
      language,
    });
    return response.data;
  },

  healthCheck: async (): Promise<{ status: string; documents_indexed: number }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
