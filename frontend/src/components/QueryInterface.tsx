import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { queryDocuments } from '../services/api';
import { QueryRequest, QueryResponse } from '../types';

interface QueryInterfaceProps {
  onQueryResult?: (result: QueryResponse) => void;
  documentId?: number;
}

const QueryInterface: React.FC<QueryInterfaceProps> = ({ onQueryResult, documentId }) => {
  const [question, setQuestion] = useState('');
  const [maxResults, setMaxResults] = useState(5);
  const [scoreThreshold, setScoreThreshold] = useState(0.7);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const queryMutation = useMutation(queryDocuments, {
    onSuccess: (data) => {
      onQueryResult?.(data);
    },
    onError: (error) => {
      console.error('Query failed:', error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) {
      alert('Please enter a question');
      return;
    }

    const queryRequest: QueryRequest = {
      question: question.trim(),
      max_results: maxResults,
      score_threshold: scoreThreshold,
    };

    if (documentId) {
      queryRequest.document_id = documentId;
    }

    queryMutation.mutate(queryRequest);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const exampleQuestions = [
    "What is the main topic of this document?",
    "Can you summarize the key points?",
    "What are the conclusions or recommendations?",
    "Who are the main people or organizations mentioned?",
  ];

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Ask a Question</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
            Your Question
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            className="input min-h-[100px] resize-y"
            placeholder="What would you like to know about your documents?"
            disabled={queryMutation.isLoading}
          />
          <p className="text-xs text-gray-500 mt-1">
            Press Enter to submit, Shift+Enter for new line
          </p>
        </div>

        {/* Advanced Options */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-primary-600 hover:text-primary-700 focus:outline-none"
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced Options
          </button>
        </div>

        {showAdvanced && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <label htmlFor="maxResults" className="block text-sm font-medium text-gray-700 mb-1">
                Max Results: {maxResults}
              </label>
              <input
                id="maxResults"
                type="range"
                min="1"
                max="10"
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value))}
                className="w-full"
              />
            </div>
            
            <div>
              <label htmlFor="scoreThreshold" className="block text-sm font-medium text-gray-700 mb-1">
                Relevance Threshold: {scoreThreshold}
              </label>
              <input
                id="scoreThreshold"
                type="range"
                min="0.3"
                max="0.9"
                step="0.1"
                value={scoreThreshold}
                onChange={(e) => setScoreThreshold(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
        )}

        <div className="flex items-center justify-between">
          <button
            type="submit"
            disabled={queryMutation.isLoading || !question.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {queryMutation.isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Processing...</span>
              </div>
            ) : (
              'Ask Question'
            )}
          </button>
          
          {documentId && (
            <span className="text-sm text-gray-500">
              Searching in specific document
            </span>
          )}
        </div>
      </form>

      {/* Example Questions */}
      {!queryMutation.isLoading && question === '' && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Example Questions:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {exampleQuestions.map((example, index) => (
              <button
                key={index}
                onClick={() => setQuestion(example)}
                className="text-left text-sm text-primary-600 hover:text-primary-700 hover:bg-primary-50 p-2 rounded border border-gray-200 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {queryMutation.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">
            Query failed: {(queryMutation.error as Error).message}
          </p>
        </div>
      )}
    </div>
  );
};

export default QueryInterface;