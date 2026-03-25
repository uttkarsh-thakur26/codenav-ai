import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const markdownComponents = {
  p:          (props) => <p className="mb-3 last:mb-0" {...props} />,
  strong:     (props) => <strong className="font-semibold text-gray-100" {...props} />,
  em:         (props) => <em className="italic" {...props} />,
  ul:         (props) => <ul className="list-disc pl-6 mb-3 space-y-1.5" {...props} />,
  ol:         (props) => <ol className="list-decimal pl-6 mb-3 space-y-1.5" {...props} />,
  li:         (props) => <li className="leading-relaxed" {...props} />,
  pre:        ({ children }) => (
    <pre className="bg-gray-950 rounded-lg p-4 mb-3 overflow-x-auto text-xs font-mono text-gray-300 leading-relaxed">
      {children}
    </pre>
  ),
  code:       ({ className, children, ...props }) => {
    const isBlock = Boolean(className);
    if (isBlock) {
      return (
        <code className={className} {...props}>
          {children}
        </code>
      );
    }
    return (
      <code className="bg-gray-700/50 text-gray-200 px-1.5 py-0.5 rounded-md text-sm font-mono" {...props}>
        {children}
      </code>
    );
  },
  blockquote: (props) => <blockquote className="border-l-2 border-indigo-500 pl-4 italic text-gray-400 mb-3" {...props} />,
  a:          (props) => <a className="text-indigo-400 underline hover:text-indigo-300" target="_blank" rel="noopener noreferrer" {...props} />,
  h1:         (props) => <h1 className="text-xl font-bold text-gray-100 mb-2 mt-4" {...props} />,
  h2:         (props) => <h2 className="text-lg font-bold text-gray-100 mb-2 mt-3" {...props} />,
  h3:         (props) => <h3 className="text-base font-semibold text-gray-100 mb-1 mt-2" {...props} />,
};

export default function Message({ role, content }) {
  const isUser = role === 'user';

  return (
    <div className={`flex gap-3 px-6 py-4 ${isUser ? 'bg-transparent' : 'bg-gray-800/40'}`}>
      {/* Avatar */}
      <div
        className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center
                     ${isUser ? 'bg-indigo-600' : 'bg-emerald-600'}`}
      >
        {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
      </div>

      {/* Body */}
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium mb-1 text-gray-400">
          {isUser ? 'You' : 'CodeNav AI'}
        </p>
        {isUser ? (
          <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap break-words">
            {content}
          </div>
        ) : (
          <div className="text-sm text-gray-200 leading-relaxed break-words space-y-2 [&>ul]:my-2 [&>ol]:my-2">
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
              {content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
