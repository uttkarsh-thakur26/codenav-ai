import { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { indexRepository, askQuestion, getRepoSummary } from './services/api';

export default function App() {
  const [isRepoIndexed, setIsRepoIndexed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleIndex = async (url) => {
    const result = await indexRepository(url);
    setIsRepoIndexed(true);
    setMessages([]);
    return result;
  };

  const handleResetActive = () => {
    setIsRepoIndexed(false);
    setMessages([]);
  };

  const handleGenerateSummary = async () => {
    if (isLoading || !isRepoIndexed) return;

    setIsLoading(true);
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: 'Please generate an Architecture Summary of this repository.' },
    ]);

    try {
      const summaryText = await getRepoSummary();
      setMessages((prev) => [...prev, { role: 'assistant', content: summaryText }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAsk = async (question) => {
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setIsLoading(true);

    try {
      const { answer } = await askQuestion(question);
      setMessages((prev) => [...prev, { role: 'assistant', content: answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100">
      <Sidebar
        onIndexed={handleIndex}
        isRepoIndexed={isRepoIndexed}
        onResetActive={handleResetActive}
        onGenerateSummary={handleGenerateSummary}
        isLoading={isLoading}
      />

      <main className="flex-1 flex flex-col min-w-0">
        <ChatWindow messages={messages} />
        <ChatInput onSend={handleAsk} disabled={!isRepoIndexed} isLoading={isLoading} />
      </main>
    </div>
  );
}
