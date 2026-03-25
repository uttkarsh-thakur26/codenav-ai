import { useEffect, useRef } from 'react';
import { MessageSquare } from 'lucide-react';
import Message from './Message';

export default function ChatWindow({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-gray-500 gap-3">
        <MessageSquare size={48} strokeWidth={1.2} />
        <p className="text-lg font-medium text-gray-400">No messages yet</p>
        <p className="text-sm">Index a repository, then ask a question to get started.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {messages.map((msg, idx) => (
        <Message key={idx} role={msg.role} content={msg.content} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
