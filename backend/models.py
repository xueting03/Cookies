from typing import List, Optional
from pydantic import BaseModel

class CommitInfo:
    def __init__(self, hash: str, author: str, message: str, line_range: Optional[tuple] = None):
        self.hash = hash
        self.author = author
        self.message = message
        self.line_range = line_range  # (start_line, end_line)

class FunctionInfo:
    def __init__(self, name: str, params: List[str], docstring: Optional[str], lineno: int, end_lineno: int, file_path: str):
        self.name = name
        self.params = params
        self.docstring = docstring
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.file_path = file_path
        self.commits: List[CommitInfo] = []

class FunctionDoc:
    def __init__(self, function_info: FunctionInfo, summary: str, stale: bool = False):
        self.function_info = function_info
        self.summary = summary
        self.stale = stale  # True if code changed after doc creation

# Pydantic models for FastAPI request validation
class RepoAnalysisRequest(BaseModel):
    repo_path: str
    file_types: Optional[List[str]] = ["java", "python", "javascript"]
    output_file: Optional[str] = "documentation.md"

class DocGenerationRequest(BaseModel):
    file_path: str
    repo_path: str
    language: str
    last_doc_commit_hash: Optional[str] = None

class IndividualDocsRequest(BaseModel):
    repo_path: str
    language: str = "java"

class ConversionRequest(BaseModel):
    folder_path: str = "documentation-generated"
    formats: Optional[List[str]] = ["docx"]

class ConversionResponse(BaseModel):
    success: bool
    message: str
    converted_files: List[dict]
    errors: List[dict]

class RepositoryRequest(BaseModel):
    repo_path: str
    language: str = "java"

class DocumentationResponse(BaseModel):
    success: bool
    message: str
    documentation_file: str
    generated_files: List[dict]
