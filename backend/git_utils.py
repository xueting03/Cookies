"""
Git utilities for commit analysis and stale documentation detection
"""
from git import Repo
from typing import List
from models import CommitInfo, FunctionInfo

class GitAnalyzer:
    @staticmethod
    def get_commits_for_function(repo_path: str, func: FunctionInfo) -> List[CommitInfo]:
        try:
            # Try to find the git repository
            git_repo_path = GitAnalyzer._find_git_repo(repo_path)
            if not git_repo_path:
                print(f"No git repository found for {repo_path}")
                return []
            
            repo = Repo(git_repo_path)
            
            # Get relative path from git root
            relative_file_path = GitAnalyzer._get_relative_path(git_repo_path, func.file_path)
            if not relative_file_path:
                print(f"Could not determine relative path for {func.file_path}")
                return []
            
            # Get commits that touched this file
            try:
                commits = list(repo.iter_commits(paths=relative_file_path, max_count=10))  # Limit to recent commits
            except Exception as e:
                print(f"Error getting commits for {relative_file_path}: {e}")
                return []
            
            relevant_commits = []
            for commit in commits[:5]:  # Only check last 5 commits for performance
                try:
                    relevant_commits.append(CommitInfo(
                        hash=commit.hexsha,
                        author=commit.author.name,
                        message=commit.message.strip(),
                        line_range=(func.lineno, func.end_lineno)
                    ))
                except Exception as e:
                    print(f"Error processing commit {commit.hexsha}: {e}")
                    continue
            
            return relevant_commits
        except Exception as e:
            print(f"Git analysis failed for {repo_path}: {e}")
            return []
    
    @staticmethod
    def _find_git_repo(start_path: str) -> str:
        """Find the git repository root starting from the given path"""
        import os
        current_path = start_path
        
        # Try the given path first
        if os.path.exists(os.path.join(current_path, '.git')):
            return current_path
        
        # Try parent directory (common case)
        parent_path = os.path.dirname(current_path)
        if os.path.exists(os.path.join(parent_path, '.git')):
            return parent_path
        
        # Try grandparent directory
        grandparent_path = os.path.dirname(parent_path)
        if os.path.exists(os.path.join(grandparent_path, '.git')):
            return grandparent_path
        
        return None
    
    @staticmethod
    def _get_relative_path(git_root: str, file_path: str) -> str:
        """Get relative path from git root to file"""
        import os
        try:
            return os.path.relpath(file_path, git_root).replace('\\', '/')
        except Exception:
            return None

    @staticmethod
    def detect_stale_doc(func: FunctionInfo, last_doc_commit_hash: str, repo_path: str = ".") -> bool:
        """Check if documentation is stale by comparing with recent commits"""
        try:
            git_repo_path = GitAnalyzer._find_git_repo(repo_path)
            if not git_repo_path:
                return False  # Can't determine staleness without git
            
            repo = Repo(git_repo_path)
            relative_file_path = GitAnalyzer._get_relative_path(git_repo_path, func.file_path)
            
            if not relative_file_path:
                return False
            
            # Check if there are commits after the last doc commit
            commits = list(repo.iter_commits(paths=relative_file_path, max_count=10))
            
            for commit in commits:
                if commit.hexsha == last_doc_commit_hash:
                    break
                # If we find commits before reaching the doc commit, docs are stale
                try:
                    if commit.parents:
                        diff = commit.diff(commit.parents[0], paths=relative_file_path)
                        if diff:  # File was modified
                            return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            print(f"Stale detection failed: {e}")
            return False
