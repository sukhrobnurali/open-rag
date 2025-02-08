import React, { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { uploadDocument } from '../services/api';
import { DocumentUploadResponse } from '../types';

interface DocumentUploadProps {
  onUploadSuccess?: (response: DocumentUploadResponse) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation(uploadDocument, {
    onSuccess: (data) => {
      setUploadProgress(null);
      queryClient.invalidateQueries('documents');
      onUploadSuccess?.(data);
    },
    onError: (error) => {
      setUploadProgress(null);
      console.error('Upload failed:', error);
    },
  });

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    // Validate file type
    const allowedTypes = ['.pdf', '.txt', '.doc', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      alert(`File type ${fileExtension} not allowed. Allowed types: ${allowedTypes.join(', ')}`);
      return;
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('File size exceeds 50MB limit');
      return;
    }

    setUploadProgress(0);
    
    // Simulate upload progress (since we can't get real progress easily)
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev === null) return null;
        const newProgress = prev + Math.random() * 30;
        return newProgress >= 90 ? 90 : newProgress;
      });
    }, 200);

    try {
      await uploadMutation.mutateAsync(file);
      clearInterval(progressInterval);
      setUploadProgress(100);
      setTimeout(() => setUploadProgress(null), 1000);
    } catch (error) {
      clearInterval(progressInterval);
      setUploadProgress(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unit = 0;
    
    while (size >= 1024 && unit < units.length - 1) {
      size /= 1024;
      unit++;
    }
    
    return `${size.toFixed(1)} ${units[unit]}`;
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Upload Document</h2>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {uploadProgress !== null ? (
          <div className="space-y-4">
            <div className="text-sm text-gray-600">Uploading...</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <div className="text-sm text-gray-500">{Math.round(uploadProgress)}%</div>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            
            <div className="space-y-2">
              <p className="text-lg font-medium">
                Drop your files here, or{' '}
                <label className="text-primary-600 hover:text-primary-700 cursor-pointer">
                  browse
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.txt,.doc,.docx"
                    onChange={handleFileInput}
                    disabled={uploadMutation.isLoading}
                  />
                </label>
              </p>
              
              <p className="text-sm text-gray-500">
                Supported formats: PDF, TXT, DOC, DOCX (max 50MB)
              </p>
            </div>
          </>
        )}
      </div>

      {uploadMutation.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">
            Upload failed: {(uploadMutation.error as Error).message}
          </p>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;