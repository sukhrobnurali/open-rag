import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import DocumentUpload from '../components/DocumentUpload';
import { 
  getDocuments, 
  processDocument, 
  deleteDocument, 
  getDocumentSummary,
  formatFileSize, 
  formatDate, 
  getStatusColor, 
  getStatusText 
} from '../services/api';
import { Document, DocumentUploadResponse, DocumentSummary } from '../types';

const DocumentsPage: React.FC = () => {
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [documentSummary, setDocumentSummary] = useState<DocumentSummary | null>(null);
  const queryClient = useQueryClient();

  const { data: documents, isLoading, error } = useQuery<Document[]>(
    'documents',
    getDocuments,
    {
      refetchInterval: 5000, // Refresh every 5 seconds to check processing status
    }
  );

  const processMutation = useMutation(processDocument, {
    onSuccess: () => {
      queryClient.invalidateQueries('documents');
    },
  });

  const deleteMutation = useMutation(deleteDocument, {
    onSuccess: () => {
      queryClient.invalidateQueries('documents');
      setSelectedDocument(null);
      setDocumentSummary(null);
    },
  });

  const summaryMutation = useMutation(getDocumentSummary, {
    onSuccess: (data) => {
      setDocumentSummary(data);
    },
  });

  const handleUploadSuccess = (response: DocumentUploadResponse) => {
    console.log('Document uploaded:', response);
    queryClient.invalidateQueries('documents');
  };

  const handleProcessDocument = async (documentId: number) => {
    try {
      await processMutation.mutateAsync(documentId);
    } catch (error) {
      console.error('Process failed:', error);
    }
  };

  const handleDeleteDocument = async (documentId: number) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteMutation.mutateAsync(documentId);
      } catch (error) {
        console.error('Delete failed:', error);
      }
    }
  };

  const handleGetSummary = async (documentId: number) => {
    try {
      await summaryMutation.mutateAsync(documentId);
    } catch (error) {
      console.error('Summary failed:', error);
    }
  };

  const DocumentCard: React.FC<{ document: Document }> = ({ document }) => (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-medium text-gray-900 truncate">
            {document.original_filename}
          </h3>
          
          <div className="mt-2 grid grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Size:</span> {formatFileSize(document.file_size)}
            </div>
            <div>
              <span className="font-medium">Type:</span> {document.file_type}
            </div>
            <div>
              <span className="font-medium">Uploaded:</span> {formatDate(document.created_at)}
            </div>
            <div>
              <span className="font-medium">Status:</span>
              <span className={`ml-1 px-2 py-1 text-xs rounded-full ${getStatusColor(document.status)}`}>
                {getStatusText(document.status)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center space-x-3">
        {document.status === 'uploaded' && (
          <button
            onClick={() => handleProcessDocument(document.id)}
            disabled={processMutation.isLoading}
            className="btn-primary text-sm"
          >
            {processMutation.isLoading ? 'Processing...' : 'Process'}
          </button>
        )}
        
        {document.status === 'completed' && (
          <>
            <button
              onClick={() => handleGetSummary(document.id)}
              disabled={summaryMutation.isLoading}
              className="btn-secondary text-sm"
            >
              {summaryMutation.isLoading ? 'Loading...' : 'Summary'}
            </button>
            
            <button
              onClick={() => setSelectedDocument(document)}
              className="btn-secondary text-sm"
            >
              Details
            </button>
          </>
        )}
        
        <button
          onClick={() => handleDeleteDocument(document.id)}
          disabled={deleteMutation.isLoading}
          className="btn text-red-600 hover:bg-red-50 text-sm"
        >
          Delete
        </button>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center text-red-600">
          <p>Error loading documents: {(error as Error).message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Document Management</h1>
        <div className="text-sm text-gray-600">
          {documents?.length || 0} documents
        </div>
      </div>

      {/* Upload Section */}
      <DocumentUpload onUploadSuccess={handleUploadSuccess} />

      {/* Documents Grid */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-gray-900">Your Documents</h2>
        
        {!documents || documents.length === 0 ? (
          <div className="card text-center text-gray-500">
            <p>No documents uploaded yet</p>
            <p className="text-sm">Upload your first document above to get started!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {documents.map((document) => (
              <DocumentCard key={document.id} document={document} />
            ))}
          </div>
        )}
      </div>

      {/* Document Summary Modal */}
      {documentSummary && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Document Summary</h3>
                <button
                  onClick={() => setDocumentSummary(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900">{documentSummary.filename}</h4>
                  <p className="text-sm text-gray-600">
                    Generated from {documentSummary.chunks_used} text chunks
                  </p>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700 whitespace-pre-wrap">
                    {documentSummary.summary}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Document Details Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Document Details</h3>
                <button
                  onClick={() => setSelectedDocument(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Original Filename</label>
                    <p className="text-sm text-gray-900">{selectedDocument.original_filename}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">File Type</label>
                    <p className="text-sm text-gray-900">{selectedDocument.file_type}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">File Size</label>
                    <p className="text-sm text-gray-900">{formatFileSize(selectedDocument.file_size)}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Status</label>
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(selectedDocument.status)}`}>
                      {getStatusText(selectedDocument.status)}
                    </span>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Upload Date</label>
                    <p className="text-sm text-gray-900">{formatDate(selectedDocument.created_at)}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Last Updated</label>
                    <p className="text-sm text-gray-900">{formatDate(selectedDocument.updated_at)}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage;