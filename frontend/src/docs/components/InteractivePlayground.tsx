import React from 'react';
import {
  SandpackProvider,
  SandpackLayout,
  SandpackCodeEditor,
  SandpackPreview,
  SandpackThemeProvider
} from '@codesandbox/sandpack-react';
import { nightOwl } from '@codesandbox/sandpack-themes';

interface InteractivePlaygroundProps {
  title?: string;
  description?: string;
  files?: Record<string, string>;
  template?: 'react' | 'vanilla' | 'vue' | 'angular';
  showPreview?: boolean;
  editorHeight?: string;
}

const defaultFiles = {
  '/App.js': `import React from 'react';
import './styles.css';

export default function App() {
  return (
    <div className="app">
      <h1>Hello Devora!</h1>
      <p>Edit this code and see the changes live.</p>
      <button onClick={() => alert('Welcome to Devora!')}>
        Click me
      </button>
    </div>
  );
}`,
  '/styles.css': `.app {
  font-family: system-ui, -apple-system, sans-serif;
  text-align: center;
  padding: 2rem;
}

h1 {
  color: #6366f1;
  margin-bottom: 1rem;
}

button {
  background: #6366f1;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover {
  background: #4f46e5;
}`
};

export const InteractivePlayground: React.FC<InteractivePlaygroundProps> = ({
  title = 'Interactive Playground',
  description,
  files = defaultFiles,
  template = 'react',
  showPreview = true,
  editorHeight = '400px'
}) => {
  return (
    <div className="my-6 border border-gray-200 rounded-lg overflow-hidden shadow-sm">
      {/* Header */}
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        {description && (
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        )}
      </div>

      {/* Sandpack */}
      <SandpackProvider
        template={template}
        files={files}
        theme={nightOwl}
        options={{
          showNavigator: false,
          showTabs: true,
          showLineNumbers: true,
          editorHeight
        }}
      >
        <SandpackThemeProvider theme={nightOwl}>
          <SandpackLayout>
            <SandpackCodeEditor
              style={{ height: editorHeight }}
              showTabs
              showLineNumbers
              showInlineErrors
              wrapContent
            />
            {showPreview && (
              <SandpackPreview
                style={{ height: editorHeight }}
                showOpenInCodeSandbox
                showRefreshButton
              />
            )}
          </SandpackLayout>
        </SandpackThemeProvider>
      </SandpackProvider>

      {/* Footer */}
      <div className="bg-gray-50 px-4 py-2 border-t border-gray-200 text-xs text-gray-500">
        Try editing the code above to see changes in real-time
      </div>
    </div>
  );
};

export default InteractivePlayground;
