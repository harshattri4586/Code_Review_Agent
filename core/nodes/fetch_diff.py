import os
from github import Github, Auth
from core.state import ReviewState, ChangedFile

def get_github_client() -> Github:
    """
    Core logic doesn't care where the token came from (GITHUB_TOKEN in
    Actions, or a pasted PAT in Streamlit) - it just reads from env.
    Each entrypoint is responsible for setting this env var before
    calling into core/.
    """
    token = os.environ["GITHUB_TOKEN"]
    return Github(auth= Auth.Token(token))

MAX_FILES = 50
MAX_TOTAL_CHANGED_LINES = 2000


def fetch_diff(state: ReviewState) -> dict:
    """
    LangGraph node: fetches the list of changed files + their diffs
    for the given PR. Skips deleted files (nothing to review).
 
    Returns a partial state update - LangGraph merges this into
    the running state automatically.
    """

    gh = get_github_client()
    repo = gh.get_repo(state["repo_name"])
    pr = repo.get_pull(state["pr_number"])

    changed_files: list[ChangedFile] = []
    skipped_files: list[str] = []
    total_changed_lines = 0

    for file in pr.get_files():
        if file.status == "removed":
            continue

        if file.patch is None:
            skipped_files.append(f"{file.filename} (binary, not reviewable)")
            continue

        file_lines = file.additions + file.deletions

        if(
            len(changed_files) >= MAX_FILES or
            total_changed_lines + file_lines > MAX_TOTAL_CHANGED_LINES
        ):
            skipped_files.append(f"{file.filename} (skipped: PR size limit reached)")
            continue

        changed_files.append(
            ChangedFile(
                filename=file.filename,
                diff_text=file.patch,
                status=file.status
            )
        )
        total_changed_lines += file_lines

    return {"changed_files": changed_files, "failed_files":skipped_files}