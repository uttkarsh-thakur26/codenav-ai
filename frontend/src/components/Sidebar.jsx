import { useState, useEffect } from 'react';
import {
  GitBranch, Loader2, CheckCircle2, AlertCircle,
  Trash2, Database, RefreshCw, FileText,
} from 'lucide-react';
import { getCachedRepos, deleteCachedRepo } from '../services/api';

export default function Sidebar({ onIndexed, isRepoIndexed, onResetActive, onGenerateSummary, isLoading }) {
  const [repoUrl, setRepoUrl] = useState('');
  const [isIndexing, setIsIndexing] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [isError, setIsError] = useState(false);
  const [cachedRepos, setCachedRepos] = useState([]);
  const [activeRepoName, setActiveRepoName] = useState(null);

  const fetchCachedRepos = async () => {
    try {
      const { repos } = await getCachedRepos();
      setCachedRepos(repos);
    } catch {
      setCachedRepos([]);
    }
  };

  useEffect(() => {
    fetchCachedRepos();
  }, []);

  const handleIndex = async () => {
    if (!repoUrl.trim() || isIndexing) return;

    setIsIndexing(true);
    setStatusMessage(null);
    setIsError(false);

    try {
      const result = await onIndexed(repoUrl.trim());
      const name = repoUrl.trim().replace(/\/+$/, '').split('/').pop().replace(/\.git$/, '');
      setActiveRepoName(name);

      if (result.cache_hit) {
        setStatusMessage(`⚡ Loaded from cache instantly (${result.indexed_chunks} chunks)`);
      } else {
        setStatusMessage(`✅ Indexed ${result.indexed_chunks} chunks successfully.`);
      }
      setIsError(false);
      await fetchCachedRepos();
    } catch (err) {
      setStatusMessage(err.message);
      setIsError(true);
    } finally {
      setIsIndexing(false);
    }
  };

  const handleLoadCached = async (repoName) => {
    if (isIndexing) return;

    setIsIndexing(true);
    setStatusMessage(null);
    setIsError(false);

    try {
      const dummyUrl = `https://github.com/cached/${repoName}`;
      const result = await onIndexed(dummyUrl);
      setActiveRepoName(repoName);

      if (result.cache_hit) {
        setStatusMessage(`⚡ Loaded ${repoName} from cache (${result.indexed_chunks} chunks)`);
      } else {
        setStatusMessage(`✅ Re-indexed ${repoName} (${result.indexed_chunks} chunks)`);
      }
      setIsError(false);
    } catch (err) {
      setStatusMessage(err.message);
      setIsError(true);
    } finally {
      setIsIndexing(false);
    }
  };

  const handleDelete = async (repoName) => {
    try {
      await deleteCachedRepo(repoName);
      await fetchCachedRepos();

      if (activeRepoName === repoName) {
        setActiveRepoName(null);
        onResetActive?.();
        setStatusMessage(null);
      }
    } catch (err) {
      setStatusMessage(err.message);
      setIsError(true);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleIndex();
  };

  return (
    <aside className="w-72 shrink-0 bg-gray-950 text-gray-300 flex flex-col h-screen border-r border-gray-800">
      {/* Header */}
      <div className="p-5 border-b border-gray-800">
        <div className="flex items-center gap-2 mb-1">
          <GitBranch size={20} className="text-indigo-400" />
          <h1 className="text-lg font-semibold text-white tracking-tight">CodeNav AI</h1>
        </div>
        <p className="text-xs text-gray-500">RAG-powered code exploration</p>
      </div>

      {/* Repo input */}
      <div className="p-4 flex flex-col gap-3">
        <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
          GitHub Repository
        </label>
        <input
          type="text"
          placeholder="https://github.com/user/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isIndexing}
          className="w-full rounded-lg bg-gray-900 border border-gray-700 px-3 py-2 text-sm
                     text-gray-200 placeholder-gray-600 outline-none
                     focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/40
                     disabled:opacity-50 transition-colors"
        />
        <button
          onClick={handleIndex}
          disabled={isIndexing || !repoUrl.trim()}
          className="w-full rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700
                     disabled:cursor-not-allowed px-4 py-2 text-sm font-medium text-white
                     transition-colors flex items-center justify-center gap-2"
        >
          {isIndexing ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Indexing...
            </>
          ) : (
            'Index Repository'
          )}
        </button>
      </div>

      {/* Generate Summary shortcut */}
      {isRepoIndexed && (
        <div className="px-4 pb-2">
          <button
            onClick={onGenerateSummary}
            disabled={isLoading || isIndexing}
            className="w-full rounded-lg border border-purple-500/40 bg-purple-600/10
                       hover:bg-purple-600/20 disabled:bg-gray-800 disabled:border-gray-700
                       disabled:cursor-not-allowed px-4 py-2 text-sm font-medium text-purple-300
                       transition-colors flex items-center justify-center gap-2"
          >
            <FileText size={15} />
            Generate Summary
          </button>
        </div>
      )}

      {/* Status feedback */}
      {statusMessage && (
        <div className={`mx-4 rounded-lg px-3 py-2 text-xs flex items-start gap-2
                         ${isError ? 'bg-red-950/50 text-red-400' : 'bg-green-950/50 text-green-400'}`}>
          {isError
            ? <AlertCircle size={14} className="mt-0.5 shrink-0" />
            : <CheckCircle2 size={14} className="mt-0.5 shrink-0" />}
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Cached repositories */}
      <div className="px-4 pt-4 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Database size={14} className="text-gray-500" />
          <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Cached Repos</span>
        </div>
        <button
          onClick={fetchCachedRepos}
          title="Refresh list"
          className="p-1 rounded hover:bg-gray-800 text-gray-500 hover:text-gray-300 transition-colors"
        >
          <RefreshCw size={12} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-1.5">
        {cachedRepos.length === 0 ? (
          <p className="text-xs text-gray-600 italic">No cached repositories yet.</p>
        ) : (
          cachedRepos.map((name) => (
            <div
              key={name}
              className={`flex items-center justify-between rounded-lg px-3 py-2 text-sm
                          transition-colors group
                          ${activeRepoName === name
                            ? 'bg-indigo-600/20 border border-indigo-500/30'
                            : 'bg-gray-900 border border-gray-800 hover:border-gray-700'}`}
            >
              <button
                onClick={() => handleLoadCached(name)}
                disabled={isIndexing}
                className="flex-1 text-left truncate text-gray-300 hover:text-white
                           disabled:opacity-50 transition-colors text-xs font-medium"
                title={`Load ${name}`}
              >
                {name}
              </button>

              <button
                onClick={() => handleDelete(name)}
                disabled={isIndexing}
                className="ml-2 shrink-0 p-1 rounded text-gray-600
                           hover:text-red-400 hover:bg-red-950/40
                           disabled:opacity-50 transition-colors opacity-0 group-hover:opacity-100"
                title={`Delete ${name}`}
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Active repo indicator */}
      {isRepoIndexed && (
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-2 text-xs text-green-400">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Repository indexed &mdash; ready to chat
          </div>
        </div>
      )}
    </aside>
  );
}
