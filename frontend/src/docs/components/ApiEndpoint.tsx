import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import CodeBlock from './CodeBlock';

interface ApiEndpointProps {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  description: string;
  parameters?: Array<{
    name: string;
    type: string;
    required: boolean;
    description: string;
  }>;
  requestBody?: {
    contentType: string;
    example: string;
  };
  response?: {
    status: number;
    description: string;
    example: string;
  };
}

const methodColors = {
  GET: 'bg-blue-100 text-blue-700 border-blue-300',
  POST: 'bg-green-100 text-green-700 border-green-300',
  PUT: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  DELETE: 'bg-red-100 text-red-700 border-red-300',
  PATCH: 'bg-purple-100 text-purple-700 border-purple-300'
};

export const ApiEndpoint: React.FC<ApiEndpointProps> = ({
  method,
  path,
  description,
  parameters,
  requestBody,
  response
}) => {
  const [copiedPath, setCopiedPath] = useState(false);

  const handleCopyPath = async () => {
    await navigator.clipboard.writeText(path);
    setCopiedPath(true);
    setTimeout(() => setCopiedPath(false), 2000);
  };

  return (
    <div className="my-6 border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
      {/* Header */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 text-xs font-bold rounded border ${methodColors[method]}`}>
            {method}
          </span>
          <code className="flex-1 text-sm font-mono text-gray-800">{path}</code>
          <button
            onClick={handleCopyPath}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            aria-label="Copy path"
          >
            {copiedPath ? (
              <Check className="w-4 h-4 text-green-600" />
            ) : (
              <Copy className="w-4 h-4 text-gray-600" />
            )}
          </button>
        </div>
        <p className="mt-2 text-sm text-gray-600">{description}</p>
      </div>

      {/* Parameters */}
      {parameters && parameters.length > 0 && (
        <div className="p-4 border-b border-gray-200">
          <h4 className="font-semibold text-sm mb-3 text-gray-900">Parameters</h4>
          <div className="space-y-2">
            {parameters.map((param, index) => (
              <div key={index} className="flex gap-2 text-sm">
                <code className="font-mono text-blue-600">{param.name}</code>
                <span className="text-gray-400">|</span>
                <span className="text-gray-600">{param.type}</span>
                {param.required && (
                  <span className="text-red-600 text-xs">required</span>
                )}
                <span className="text-gray-500">- {param.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Request Body */}
      {requestBody && (
        <div className="p-4 border-b border-gray-200">
          <h4 className="font-semibold text-sm mb-3 text-gray-900">Request Body</h4>
          <span className="text-xs text-gray-500 mb-2 block">{requestBody.contentType}</span>
          <CodeBlock code={requestBody.example} language="json" />
        </div>
      )}

      {/* Response */}
      {response && (
        <div className="p-4">
          <h4 className="font-semibold text-sm mb-3 text-gray-900">
            Response <span className="text-green-600">{response.status}</span>
          </h4>
          <p className="text-sm text-gray-600 mb-3">{response.description}</p>
          <CodeBlock code={response.example} language="json" />
        </div>
      )}
    </div>
  );
};

export default ApiEndpoint;
