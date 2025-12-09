import React, { useState } from 'react';
import { Check, Copy } from 'lucide-react';

interface CodeBlockProps {
  code: string;
  language?: string;
  fileName?: string;
  showLineNumbers?: boolean;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = 'javascript',
  fileName,
  showLineNumbers = false
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = code.split('\n');

  return (
    <div className="my-4 rounded-lg border border-gray-700 bg-gray-900 overflow-hidden">
      {fileName && (
        <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
          <span className="text-sm text-gray-400 font-mono">{fileName}</span>
          <span className="text-xs text-gray-500 uppercase">{language}</span>
        </div>
      )}

      <div className="relative">
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 p-2 rounded-md bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
          aria-label="Copy code"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-500" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>

        <pre className="p-4 overflow-x-auto text-sm">
          <code className={`language-${language}`}>
            {showLineNumbers ? (
              <div className="flex">
                <div className="select-none pr-4 text-gray-600 text-right">
                  {lines.map((_, i) => (
                    <div key={i}>{i + 1}</div>
                  ))}
                </div>
                <div className="flex-1">
                  {lines.map((line, i) => (
                    <div key={i}>{line}</div>
                  ))}
                </div>
              </div>
            ) : (
              code
            )}
          </code>
        </pre>
      </div>
    </div>
  );
};

export default CodeBlock;
