export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface DocumentUploadResponse {
  document_id: number;
  filename: string;
  status: string;
  message: string;
}

export interface QueryRequest {
  question: string;
  document_id?: number;
  max_results?: number;
  score_threshold?: number;
}

export interface SourceInfo {
  document_id: number;
  chunk_index: number;
  content: string;
  score: number;
  filename: string;
  file_type: string;
}

export interface QueryResponse {
  question: string;
  answer: string;
  sources: SourceInfo[];
  processing_time_ms: number;
}

export interface DocumentSummary {
  document_id: number;
  filename: string;
  summary: string;
  chunks_used: number;
}