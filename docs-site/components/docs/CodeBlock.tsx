'use client';

import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';

interface CodeBlockProps {
  code: string;
  language: 'javascript' | 'python' | 'bash' | 'json';
  title?: string;
  showLineNumbers?: boolean;
}

export default function CodeBlock({
  code,
  language,
  title,
  showLineNumbers = true,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-6 rounded-xl overflow-hidden border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-900 border-b border-gray-700">
        <div className="flex items-center gap-2">
          {title && (
            <span className="text-sm font-medium text-gray-300">{title}</span>
          )}
          <span className="text-xs text-gray-500 uppercase">{language}</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-300 hover:text-white transition-colors rounded-lg hover:bg-gray-800"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              <span>복사됨!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>복사</span>
            </>
          )}
        </button>
      </div>

      {/* Code */}
      <div className="overflow-x-auto">
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus}
          showLineNumbers={showLineNumbers}
          customStyle={{
            margin: 0,
            padding: '1.5rem',
            background: '#1e1e1e',
            fontSize: '0.875rem',
            lineHeight: '1.7',
          }}
          lineNumberStyle={{
            minWidth: '2.5em',
            paddingRight: '1em',
            color: '#858585',
            userSelect: 'none',
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
