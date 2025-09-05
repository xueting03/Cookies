"""
Python AST parsing for function extraction
"""
import ast
from typing import List
from models import FunctionInfo

class PythonParser:
    @staticmethod
    def parse_file(file_path: str) -> List[FunctionInfo]:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read(), filename=file_path)
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func = FunctionInfo(
                    name=node.name,
                    params=[arg.arg for arg in node.args.args],
                    docstring=ast.get_docstring(node),
                    lineno=node.lineno,
                    end_lineno=getattr(node, "end_lineno", node.lineno),
                    file_path=file_path
                )
                functions.append(func)
        return functions
