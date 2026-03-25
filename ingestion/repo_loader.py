import os
import subprocess

from git import Repo
from git.exc import GitCommandError

REPOS_DIR = os.path.join(os.getcwd(), "data", "repos")
os.makedirs(REPOS_DIR, exist_ok=True)


def _extract_repo_name(repo_url: str) -> str:
    cleaned = repo_url.strip().rstrip("/")
    name = cleaned.rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    if not name:
        raise ValueError(f"Could not determine repository name from URL: {repo_url}")
    return name


def clone_github_repo(repo_url: str) -> tuple[str, bool]:
    """
    Clone or update a public GitHub repository in persistent local storage.

    Returns:
        tuple[str, bool]:
            - Absolute path to the local repository.
            - True if repository content changed (fresh clone or new commits pulled),
              False if already up to date.

    Raises:
        ValueError: If the URL is empty.
        RuntimeError: If clone/pull fails.
    """
    if not repo_url or not repo_url.strip():
        raise ValueError("Repository URL cannot be empty.")

    repo_name = _extract_repo_name(repo_url)
    repo_path = os.path.join(REPOS_DIR, repo_name)
    repo_path_abs = os.path.abspath(repo_path)

    try:
        if os.path.isdir(repo_path_abs):
            result = subprocess.run(
                ["git", "-C", repo_path_abs, "pull"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"Failed to pull repository '{repo_url}': {result.stderr or result.stdout}"
                )
            if "Already up to date" in result.stdout:
                return repo_path_abs, False
            return repo_path_abs, True

        Repo.clone_from(repo_url.strip(), repo_path_abs)
        return repo_path_abs, True
    except GitCommandError as exc:
        raise RuntimeError(f"Failed to sync repository '{repo_url}': {exc}") from exc
