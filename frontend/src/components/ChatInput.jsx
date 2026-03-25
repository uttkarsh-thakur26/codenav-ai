import { useState } from 'react';
import { SendHorizonal, Loader2 } from 'lucide-react';

export default function ChatInput({ onSend, disabled, isLoading }) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim() || disabled || isLoading) return;

    onSend(question.trim());
    setQuestion('');
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-gray-800 bg-gray-900 p-4 flex items-center gap-3"
    >
      <input
        type="text"
        placeholder={disabled ? 'Index a repository first...' : 'Ask about the codebase...'}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={disabled || isLoading}
        className="flex-1 rounded-lg bg-gray-800 border border-gray-700 px-4 py-2.5 text-sm
                   text-gray-200 placeholder-gray-500 outline-none
                   focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/40
                   disabled:opacity-50 transition-colors"
      />
      <button
        type="submit"
        disabled={disabled || isLoading || !question.trim()}
        className="shrink-0 rounded-lg bg-indigo-600 hover:bg-indigo-500
                   disabled:bg-gray-700 disabled:cursor-not-allowed
                   p-2.5 text-white transition-colors"
      >
        {isLoading ? <Loader2 size={18} className="animate-spin" /> : <SendHorizonal size={18} />}
      </button>
    </form>
  );
}
