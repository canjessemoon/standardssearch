import axios from 'axios';

const API_BASE_URL = (typeof process !== 'undefined' && process.env && process.env.NEXT_PUBLIC_API_URL)
  ? `${process.env.NEXT_PUBLIC_API_URL}/api`
  : 'http://localhost:5000/api';

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
