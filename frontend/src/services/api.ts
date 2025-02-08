import axios from 'axios';
import { 
  Document, 
  DocumentUploadResponse, 
  QueryRequest, 
  QueryResponse,
  DocumentSummary 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    
    if (error.response?.status === 404) {
      throw new Error('Resource not found');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Bad request');
    } else if (error.response?.status === 500) {
      throw new Error('Server error occurred');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout');
    } else {
      throw new Error(error.response?.data?.detail || error.message || 'Unknown error');
    }
  }
);

// Health check
export const checkHealth = async (): Promise<any> => {
  const response = await api.get('/api/v1/health');
  return response.data;
};

// Document APIs
export const uploadDocument = async (file: File): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/v1/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getDocuments = async (): Promise<Document[]> => {
  const response = await api.get('/api/v1/documents/');
  return response.data;
};

export const getDocument = async (documentId: number): Promise<Document> => {
  const response = await api.get(`/api/v1/documents/${documentId}`);
  return response.data;
};

export const processDocument = async (documentId: number): Promise<any> => {
  const response = await api.post(`/api/v1/documents/${documentId}/process`);
  return response.data;
};

export const deleteDocument = async (documentId: number): Promise<any> => {
  const response = await api.delete(`/api/v1/documents/${documentId}`);
  return response.data;
};

export const getDocumentChunks = async (documentId: number): Promise<any> => {
  const response = await api.get(`/api/v1/documents/${documentId}/chunks`);
  return response.data;
};

export const getDocumentSummary = async (documentId: number): Promise<DocumentSummary> => {
  const response = await api.get(`/api/v1/documents/${documentId}/summary`);
  return response.data;
};

// Query APIs
export const queryDocuments = async (queryRequest: QueryRequest): Promise<QueryResponse> => {
  const response = await api.post('/api/v1/query/', queryRequest);
  return response.data;
};

export const checkQueryHealth = async (): Promise<any> => {
  const response = await api.get('/api/v1/query/health');
  return response.data;
};

// Utility functions
export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unit = 0;
  
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit++;
  }
  
  return `${size.toFixed(1)} ${units[unit]}`;
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'text-green-600 bg-green-50';
    case 'processing':
      return 'text-blue-600 bg-blue-50';
    case 'failed':
      return 'text-red-600 bg-red-50';
    case 'uploaded':
      return 'text-yellow-600 bg-yellow-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
};

export const getStatusText = (status: string): string => {
  switch (status) {
    case 'uploaded':
      return 'Ready to Process';
    case 'processing':
      return 'Processing...';
    case 'completed':
      return 'Ready';
    case 'failed':
      return 'Failed';
    default:
      return status;
  }
};