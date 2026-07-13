from typing import TypedDict, Annotated, Literal
import operator

class ChangedFile(TypedDict):
    filename: str
    diff_text: str
    status: Literal["added", "modified", "deleted"]

class StaticWarning(TypedDict):
    line: int
    tool: str
    severity: str
    message: str

class FileReview(TypedDict):
    filename: str
    llm_comments: str
    success: bool

class ReviewState(TypedDict):
    ## identity/idempotency  fields
    repo_name: str
    pr_number: int
    commit_sha: str

    ## fetch diff output
    changed_files: list[ChangedFile]

    ## fetch context output
    static_analysis_output: dict[str, list[StaticWarning]]

    ## review_files output (accumulates!)
    file_reviews = Annotated[list[FileReview], operator.add]

    ## aggregate_results output (single write)
    final_summary: str
    
    ## graceful degradation tracking
    failed_files: Annotated[list[str], operator.add]