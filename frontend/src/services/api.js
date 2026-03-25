const BASE_URL = '/api';

export async function indexRepository(url) {
  try {
    const response = await fetch(`${BASE_URL}/index_repo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Indexing failed (HTTP ${response.status})`);
    }

    return await response.json();
  } catch (err) {
    throw new Error(err.message || 'Network error while indexing the repository.');
  }
}

export async function askQuestion(question) {
  try {
    const response = await fetch(`${BASE_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Query failed (HTTP ${response.status})`);
    }

    return await response.json();
  } catch (err) {
    throw new Error(err.message || 'Network error while asking the question.');
  }
}

export async function getCachedRepos() {
  try {
    const response = await fetch(`${BASE_URL}/cached_repos`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to fetch cached repos (HTTP ${response.status})`);
    }

    return await response.json();
  } catch (err) {
    throw new Error(err.message || 'Network error while fetching cached repos.');
  }
}

export async function getRepoSummary() {
  try {
    const response = await fetch(`${BASE_URL}/repo_summary`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to generate summary (HTTP ${response.status})`);
    }

    const data = await response.json();
    return data.summary;
  } catch (err) {
    throw new Error(err.message || 'Network error while generating summary.');
  }
}

export async function deleteCachedRepo(repoName) {
  try {
    const response = await fetch(`${BASE_URL}/cached_repos/${encodeURIComponent(repoName)}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Failed to delete repo (HTTP ${response.status})`);
    }

    return await response.json();
  } catch (err) {
    throw new Error(err.message || 'Network error while deleting the repo.');
  }
}
