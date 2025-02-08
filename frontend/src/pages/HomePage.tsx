import React, { useState } from 'react';
import QueryInterface from '../components/QueryInterface';
import ResultsDisplay from '../components/ResultsDisplay';
import { QueryResponse } from '../types';

const HomePage: React.FC = () => {
  const [queryResults, setQueryResults] = useState<QueryResponse[]>([]);

  const handleQueryResult = (result: QueryResponse) => {
    setQueryResults(prev => [result, ...prev]);
  };

  const clearResults = () => {
    setQueryResults([]);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          Ask Questions About Your Documents
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Upload your documents and get AI-powered answers with source citations. 
          Perfect for research, analysis, and document exploration.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600">PDF</div>
          <div className="text-sm text-gray-600">Supported format</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600">AI</div>
          <div className="text-sm text-gray-600">Powered by GPT-4</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-primary-600">Fast</div>
          <div className="text-sm text-gray-600">Quick responses</div>
        </div>
      </div>

      {/* Query Interface */}
      <QueryInterface onQueryResult={handleQueryResult} />

      {/* Results Section */}
      {queryResults.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">
              Query Results ({queryResults.length})
            </h2>
            <button
              onClick={clearResults}
              className="btn-secondary text-sm"
            >
              Clear Results
            </button>
          </div>
          
          <ResultsDisplay results={queryResults} />
        </div>
      )}

      {/* Getting Started */}
      {queryResults.length === 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Getting Started</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                1
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Upload Documents</h3>
                <p className="text-sm text-gray-600">
                  Go to the Documents page and upload your PDF or text files.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                2
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Process Documents</h3>
                <p className="text-sm text-gray-600">
                  Wait for the system to process and index your documents.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                3
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Ask Questions</h3>
                <p className="text-sm text-gray-600">
                  Use the form above to ask questions about your documents.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;