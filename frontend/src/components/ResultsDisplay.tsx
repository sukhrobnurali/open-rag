import React, { useState } from 'react';
import { QueryResponse, SourceInfo } from '../types';

interface ResultsDisplayProps {
  results: QueryResponse[];
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const [expandedSources, setExpandedSources] = useState<{ [key: string]: boolean }>({});

  const toggleSourceExpansion = (resultIndex: number, sourceIndex: number) => {
    const key = `${resultIndex}-${sourceIndex}`;
    setExpandedSources(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const formatProcessingTime = (ms: number): string => {
    if (ms < 1000) {
      return `${ms}ms`;
    } else {
      return `${(ms / 1000).toFixed(1)}s`;
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const SourceCard: React.FC<{ 
    source: SourceInfo; 
    index: number; 
    resultIndex: number; 
  }> = ({ source, index, resultIndex }) => {
    const key = `${resultIndex}-${index}`;
    const isExpanded = expandedSources[key];
    const previewLength = 150;
    const shouldTruncate = source.content.length > previewLength;

    return (
      <div className="border border-gray-200 rounded-lg p-4 space-y-3">
        {/* Source Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-700">
                {source.filename}
              </span>
              <span className="text-xs text-gray-500">
                ({source.file_type})
              </span>
            </div>
            
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
              getScoreColor(source.score)
            }`}>
              {Math.round(source.score * 100)}% match
            </span>
          </div>
          
          <span className="text-xs text-gray-400">
            Chunk #{source.chunk_index + 1}
          </span>
        </div>

        {/* Source Content */}
        <div className="text-sm text-gray-700">
          {shouldTruncate && !isExpanded ? (
            <div>
              <p>{source.content.substring(0, previewLength)}...</p>
              <button
                onClick={() => toggleSourceExpansion(resultIndex, index)}
                className="text-primary-600 hover:text-primary-700 text-xs mt-2 focus:outline-none"
              >
                Show more
              </button>
            </div>
          ) : (
            <div>
              <p className="whitespace-pre-wrap">{source.content}</p>
              {shouldTruncate && (
                <button
                  onClick={() => toggleSourceExpansion(resultIndex, index)}
                  className="text-primary-600 hover:text-primary-700 text-xs mt-2 focus:outline-none"
                >
                  Show less
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  if (results.length === 0) {
    return (
      <div className="card text-center text-gray-500">
        <div className="space-y-2">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p>No questions asked yet</p>
          <p className="text-sm">Upload some documents and ask a question to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {results.map((result, resultIndex) => (
        <div key={resultIndex} className="card">
          {/* Question */}
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Q: {result.question}
            </h3>
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span>Processing time: {formatProcessingTime(result.processing_time_ms)}</span>
              <span>{result.sources.length} sources found</span>
            </div>
          </div>

          {/* Answer */}
          <div className="mb-6">
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-blue-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a.75.75 0 01.75.75v6.5a.75.75 0 01-1.5 0v-4.69L8.05 9.8a.75.75 0 01-1.1-1.02l1.25-1.25a3 3 0 014.2 0l1.25 1.25a.75.75 0 01-1.1 1.02L11.5 8.56V13.25a.75.75 0 01-.75.75z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-blue-800">Answer:</p>
                  <div className="text-sm text-blue-700 mt-1 whitespace-pre-wrap">
                    {result.answer}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sources */}
          {result.sources.length > 0 && (
            <div>
              <h4 className="text-md font-semibold text-gray-900 mb-3">
                Sources ({result.sources.length})
              </h4>
              <div className="space-y-3">
                {result.sources.map((source, sourceIndex) => (
                  <SourceCard
                    key={sourceIndex}
                    source={source}
                    index={sourceIndex}
                    resultIndex={resultIndex}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ResultsDisplay;