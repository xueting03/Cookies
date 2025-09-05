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
    
    def generate_function_doc(self, func: FunctionInfo) -> str:
        # Safe commit links generation
        commit_links = ""
        if func.commits:
            commit_links = "\n".join([
                f"- [{c.hash[:7] if hasattr(c, 'hash') else 'unknown'}]: {c.message if hasattr(c, 'message') else 'No message'}"
                for c in func.commits
            ])
        else:
            commit_links = "No recent commits found"
        
        file_link = f"[{func.file_path}#L{func.lineno}-L{func.end_lineno}]({func.file_path}#L{func.lineno}-L{func.end_lineno})"
        
        # Try to use OpenAI API if available, otherwise fall back to template
        if self.api_key:
            try:
                return self._generate_openai_docs(func, file_link, commit_links)
            except Exception as e:
                return self._generate_template_docs(func, file_link, commit_links, f"OpenAI API failed: {str(e)}")
        else:
            return self._generate_template_docs(func, file_link, commit_links, "No valid OpenAI API key found")
    
    def _generate_openai_docs(self, func: FunctionInfo, file_link: str, commit_links: str) -> str:
        """Generate documentation using OpenAI API (v0.28 syntax)"""
        prompt = f"""Generate professional starter documentation for this function in markdown format.

Function Name: {func.name}
Parameters: {', '.join(func.params) if func.params else 'None'}
Docstring: {func.docstring or 'None'}
File: {file_link}
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
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    @staticmethod
    def _generate_template_docs(func: FunctionInfo, file_link: str, commit_links: str, error: str = None) -> str:
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
        
        return f"""# {func.name}
{error_section}
{docstring_section}
{params_section}
## File Location

{file_link}

## Recent Commits

{commit_links if commit_links else "No recent commits found"}

## Usage Example

```python
# Example usage needed
result = {func.name}({', '.join(func.params) if func.params else ''})
```

## Notes

- Function defined at lines {func.lineno}-{func.end_lineno}
- Auto-generated documentation
"""
