"""
Java parsing for function extraction
Note: Install javalang for better parsing: pip install javalang
"""
import re
from typing import List
from models import FunctionInfo

class JavaParser:
    @staticmethod
    def parse_file(file_path: str) -> List[FunctionInfo]:
        try:
            # Try using javalang if available
            import javalang
            return JavaParser._parse_with_javalang(file_path)
        except ImportError:
            # Fallback to regex parsing
            return JavaParser._parse_with_regex(file_path)
    
    @staticmethod
    def _parse_with_javalang(file_path: str) -> List[FunctionInfo]:
        """Parse using javalang library"""
        import javalang
        
        with open(file_path, "r", encoding='utf-8') as f:
            code = f.read()

        tree = javalang.parse.parse(code)
        functions = []

        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            functions.append(FunctionInfo(
                name=node.name,
                params=[p.name for p in node.parameters],
                docstring=None,  # JavaDoc extraction can be added later
                lineno=node.position.line if node.position else 0,
                end_lineno=node.position.line + 5,  # Approximation, can enhance with parsing
                file_path=file_path
            ))
        return functions
    
    @staticmethod
    def _parse_with_regex(file_path: str) -> List[FunctionInfo]:
        """Fallback regex-based parsing"""
        with open(file_path, "r", encoding='utf-8') as f:
            content = f.read()
        
        functions = []
        lines = content.split('\n')
        
        # Pattern for Java methods
        method_pattern = r'(?:public|private|protected|static|\s)*\s+\w+\s+(\w+)\s*\(([^)]*)\)\s*\{'
        
        for i, line in enumerate(lines):
            match = re.search(method_pattern, line)
            if match:
                name = match.group(1)
                params_str = match.group(2)
                params = [p.strip().split()[-1] for p in params_str.split(',') if p.strip()]
                
                # Find end line (simplified)
                end_line = JavaParser._find_method_end(lines, i)
                
                functions.append(FunctionInfo(
                    name=name,
                    params=params,
                    docstring=None,
                    lineno=i + 1,
                    end_lineno=end_line,
                    file_path=file_path
                ))
        
        return functions
    
    @staticmethod
    def _find_method_end(lines: List[str], start_line: int) -> int:
        """Find the end line of a method by counting braces"""
        brace_count = 0
        for i in range(start_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and '{' in lines[start_line]:
                return i + 1
        return start_line + 1  # Fallback
