"""
LLM API integration for generating markdown documentation
"""
import os
from typing import Optional
from models import FunctionInfo, CommitInfo
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DocGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        # Set up OpenAI API key
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_function_doc(self, func: FunctionInfo, target_format: str = "markdown") -> str:
        # Safe commit links generation
        commit_links = ""
        if func.commits:
            commit_links = "\n".join([
                f"- [{c.hash[:7] if hasattr(c, 'hash') else 'unknown'}]: {c.message if hasattr(c, 'message') else 'No message'}"
                for c in func.commits
            ])
        else:
            commit_links = "No recent commits found"
        
        # Generate format-specific links
        file_links = self._generate_file_links(func, target_format)
        
        # Try to use OpenAI API if available, otherwise fall back to template
        if self.api_key:
            try:
                return self._generate_openai_docs(func, file_links, commit_links, target_format)
            except Exception as e:
                return self._generate_template_docs(func, file_links, commit_links, target_format, f"OpenAI API failed: {str(e)}")
        else:
            return self._generate_template_docs(func, file_links, commit_links, target_format, "No valid OpenAI API key found")
    
    def _generate_file_links(self, func: FunctionInfo, target_format: str = "markdown") -> dict:
        """Generate format-specific clickable links for the function"""
        file_path = func.file_path.replace('\\', '/')
        
        # Convert to absolute path for VS Code links
        abs_path = os.path.abspath(file_path).replace('\\', '/')
        folder_path = os.path.dirname(abs_path)
        
        base_links = {
            'relative_path': file_path,
            'abs_path': abs_path,
            'folder_path': folder_path
        }
        
        if target_format.lower() == "word":
            # Only Word-compatible links (file protocol only)
            return {
                **base_links,
                'file_url': f"file:///{abs_path}",
                'folder_url': f"file:///{folder_path}"
            }
        else:
            # Full markdown links including VS Code
            return {
                **base_links,
                'vscode_file': f"vscode://file/{abs_path}",
                'vscode_line': f"vscode://file/{abs_path}:{func.lineno}",
                'vscode_range': f"vscode://file/{abs_path}:{func.lineno}",
                'file_url': f"file:///{abs_path}",
                'folder_url': f"file:///{folder_path}",
                'github_line': f"#L{func.lineno}" + (f"-L{func.end_lineno}" if func.end_lineno != func.lineno else "")
            }
    
    def _generate_openai_docs(self, func: FunctionInfo, file_links: dict, commit_links: str, target_format: str = "markdown") -> str:
        """Generate documentation using OpenAI API (v0.28 syntax)"""
        prompt = f"""Generate professional starter documentation for this function in markdown format.

Function Name: {func.name}
Parameters: {', '.join(func.params) if func.params else 'None'}
Docstring: {func.docstring or 'None'}
File: {file_links['relative_path']} (lines {func.lineno}-{func.end_lineno})
Recent Commits: {commit_links}

Please provide:
1. A clear description of what the function does
2. Parameter descriptions if any
3. Usage example
4. Any important notes

Format in clean markdown with proper headings."""

        try:
            # OpenAI 0.28 syntax
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            # Add the format-specific links section to the AI-generated content
            ai_content = response.choices[0].message.content
            
            links_section = self._generate_links_section(func, file_links, target_format)
            
            return ai_content + links_section
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def _generate_links_section(self, func: FunctionInfo, file_links: dict, target_format: str) -> str:
        """Generate format-specific links section"""
        if target_format.lower() == "word":
            # Word-only links
            return f"""

## 🔗 Quick Access

### Open Files
- 📄 [**Open File**]({file_links['file_url']}) - Open in default editor
- 📂 [**Open Folder**]({file_links['folder_url']}) - Open containing folder

### File Information
- � **File**: `{file_links['relative_path']}`
- �📏 **Lines**: {func.lineno}-{func.end_lineno}
- 🔢 **Function Length**: {func.end_lineno - func.lineno + 1} lines
"""
        else:
            # Markdown with VS Code links
            return f"""

## 🔗 Quick Access

### Open in Editor
- MARKDOWN:
- 🚀 [**Open in VS Code**]({file_links['vscode_file']}) - Open file
- 📍 [**Jump to Function**]({file_links['vscode_line']}) - Go to line {func.lineno}
- WORD DOC:
- 📄 [**Open File**]({file_links['file_url']}) - Open in default editor
- 📂 [**Open Folder**]({file_links['folder_url']}) - Open containing folder

### File Information
- 📁 **File**: `{file_links['relative_path']}`
- 📏 **Lines**: {func.lineno}-{func.end_lineno}
- 🔢 **Function Length**: {func.end_lineno - func.lineno + 1} lines
"""
    
    @staticmethod
    def _generate_template_docs(func: FunctionInfo, file_links: dict, commit_links: str, target_format: str = "markdown", error: str = None) -> str:
        """Generate template documentation when LLM is not available"""
        error_section = f"\n## Note\nLLM API not configured or failed: {error}\n" if error else ""
        
        params_section = ""
        if func.params:
            params_section = "\n## Parameters\n\n"
            for param in func.params:
                params_section += f"- **{param}**: Description needed\n"
        
        docstring_section = ""
        if func.docstring:
            docstring_section = f"\n## Description\n\n{func.docstring}\n"
        else:
            docstring_section = "\n## Description\n\n[Add description here]\n"
        
        # Enhanced file links section
        links_section = f"""## 🔗 Quick Access

### Open in Editor
- 🚀 [**Open in VS Code**]({file_links['vscode_file']}) - Open file
- 📍 [**Jump to Function**]({file_links['vscode_line']}) - Go to line {func.lineno}
- 📄 [**Open in Default Editor**]({file_links['file_protocol']}) - System default

### File Information
- 📁 **File**: `{file_links['relative_path']}`
- 📏 **Lines**: {func.lineno}-{func.end_lineno}
- 🔢 **Function Length**: {func.end_lineno - func.lineno + 1} lines
"""
        
        return f"""# {func.name}
{error_section}
{docstring_section}
{params_section}
{links_section}

## Recent Commits

{commit_links if commit_links else "No recent commits found"}

## Usage Example

```java
// Example usage needed
{func.name}({', '.join(func.params) if func.params else ''});
```

## Notes

- Function defined at lines {func.lineno}-{func.end_lineno}
- Auto-generated documentation
- Click the links above to jump directly to the code!
"""
