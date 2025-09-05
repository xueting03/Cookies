"""
JavaScript/TypeScript parsing for function extraction
"""
from typing import List
from models import FunctionInfo
import subprocess
import json
import re

class JSParser:
    """
    Uses regex-based parsing for JS files to extract functions
    For production use, consider using Babel parser via CLI or esprima
    """

    @staticmethod
    def parse_file(file_path: str) -> List[FunctionInfo]:
        with open(file_path, "r", encoding='utf-8') as f:
            content = f.read()
        
        functions = []
        lines = content.split('\n')
        
        # Patterns for different function types
        patterns = [
            # function declaration: function name() {}
            r'function\s+(\w+)\s*\(([^)]*)\)',
            # arrow function: const name = () => {}
            r'(?:const|let|var)\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*\{',
            # method in object/class: name() {}
            r'(\w+)\s*\(([^)]*)\)\s*\{'
        ]
        
        for i, line in enumerate(lines):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    name = match.group(1)
                    params_str = match.group(2) if len(match.groups()) > 1 else ""
                    params = [p.strip() for p in params_str.split(',') if p.strip()]
                    
                    # Find end line (simplified - count braces)
                    end_line = JSParser._find_function_end(lines, i)
                    
                    functions.append(FunctionInfo(
                        name=name,
                        params=params,
                        docstring=None,  # Could extract JSDoc here
                        lineno=i + 1,
                        end_lineno=end_line,
                        file_path=file_path
                    ))
        
        return functions
    
    @staticmethod
    def _find_function_end(lines: List[str], start_line: int) -> int:
        """Find the end line of a function by counting braces"""
        brace_count = 0
        for i in range(start_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and '{' in lines[start_line]:
                return i + 1
        return start_line + 1  # Fallback
