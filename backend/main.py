from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
from datetime import datetime

# Import parsers and services
from parsers.python_parser import PythonParser
from parsers.js_parser import JSParser
from parsers.java_parser import JavaParser
from git_utils import GitAnalyzer
from doc_generator import DocGenerator
from models import FunctionDoc, FunctionInfo
from services.repo_scanner import RepoScanner
from services.document_converter import DocumentConverter

# Initialize FastAPI app
app = FastAPI(
    title="Starter Doc Generator", 
    version="1.0.0",
    description="AI-powered documentation generator for code repositories"
)

# Initialize services
doc_generator = DocGenerator()
repo_scanner = RepoScanner()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported parsers mapping
PARSERS = {
    "py": PythonParser,
    "python": PythonParser,
    "js": JSParser,
    "jsx": JSParser,
    "ts": JSParser,
    "tsx": JSParser,
    "javascript": JSParser,
    "typescript": JSParser,
    "java": JavaParser
}

# ===== CORE API ENDPOINTS =====

@app.get("/")
async def root():
    """API health check and info"""
    return {
        "message": "Starter Doc Generator API",
        "status": "active",
        "documentation_structure": {
            "complete_docs": "documentation-generated/complete/",
            "individual_docs": "documentation-generated/individual/",
            "readme": "documentation-generated/README.md"
        },
        "endpoints": {
            "repository_analysis": "/scan-repository",
            "individual_docs": "/generate-individual-docs", 
            "complete_docs": "/generate-complete-repo-docs",
            "single_file_docs": "/generate-docs",
            "function_analysis": "/analyze-functions",
            "document_conversion": {
                "word_conversion": "/convert-docs-to-word", 
                "single_file": "/convert-single-file"
            },
            "test_all": "/test-all",
            "supported_languages": "/supported-languages"
        }
    }

@app.get("/supported-languages")
def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        "languages": list(set(PARSERS.keys())),
        "primary_languages": ["python", "java", "javascript", "typescript"]
    }

# ===== REPOSITORY ANALYSIS =====

@app.get("/scan-repository")
def scan_repository(repo_path: str):
    """Scan repository structure and analyze codebase architecture"""
    try:
        if not os.path.exists(repo_path):
            raise HTTPException(status_code=404, detail=f"Repository not found: {repo_path}")
        
        structure = repo_scanner.scan_repository(repo_path)
        return {
            "success": True,
            "repository_path": repo_path,
            "analysis": structure
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository scan failed: {str(e)}")

@app.get("/analyze-functions")
def analyze_functions(file_path: str, repo_path: str, language: str):
    """Analyze functions in a specific file without generating documentation"""
    try:
        # Normalize language parameter
        lang_key = language.lower()
        parser_class = PARSERS.get(lang_key)
        if not parser_class:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

        # Validate file path
        full_path = os.path.join(repo_path, file_path) if not os.path.isabs(file_path) else file_path
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        # Parse functions
        parser = parser_class()
        functions = parser.parse_file(full_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "language": language,
            "function_count": len(functions),
            "functions": [
                {
                    "name": func.name,
                    "parameters": func.params,
                    "line_range": f"{func.lineno}-{func.end_lineno}",
                    "has_docstring": bool(func.docstring),
                    "docstring": func.docstring
                }
                for func in functions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Function analysis failed: {str(e)}")

# ===== DOCUMENTATION GENERATION =====

@app.post("/generate-docs")
def generate_docs(file_path: str, repo_path: str, language: str, last_doc_commit_hash: Optional[str] = None):
    """Generate AI-powered documentation for functions in a specific file"""
    try:
        # Normalize and validate language
        lang_key = language.lower()
        parser_class = PARSERS.get(lang_key)
        if not parser_class:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

        # Validate file path
        full_path = os.path.join(repo_path, file_path) if not os.path.isabs(file_path) else file_path
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        # Parse functions
        parser = parser_class()
        functions = parser.parse_file(full_path)
        docs = []

        for func in functions:
            try:
                # Add git commit analysis (with fallback)
                try:
                    func.commits = GitAnalyzer.get_commits_for_function(repo_path, func)
                except Exception:
                    func.commits = []  # Continue without git history
                
                # Generate AI documentation (with fallback)
                try:
                    summary = doc_generator.generate_function_doc(func)
                except Exception:
                    # Fallback template
                    summary = f"""# {func.name}

## Description
Function '{func.name}' with {len(func.params)} parameter(s)

## Parameters
{chr(10).join([f"- **{param}**: Parameter description needed" for param in func.params]) if func.params else "No parameters"}

## Location
- **File:** {func.file_path}
- **Lines:** {func.lineno}-{func.end_lineno}

## Docstring
{func.docstring or "No docstring available"}
"""
                
                # Check for stale documentation
                stale = False
                if last_doc_commit_hash:
                    try:
                        stale = GitAnalyzer.detect_stale_doc(func, last_doc_commit_hash, repo_path)
                    except Exception:
                        stale = False
                
                docs.append(FunctionDoc(func, summary, stale))
                
            except Exception as e:
                print(f"Error processing function {func.name}: {e}")
                continue
        
        return {
            "success": True,
            "file_path": file_path,
            "language": language,
            "functions_documented": len(docs),
            "documentation": [
                {
                    "function_name": doc.function_info.name,
                    "parameters": doc.function_info.params,
                    "line_range": f"{doc.function_info.lineno}-{doc.function_info.end_lineno}",
                    "documentation": doc.summary,
                    "is_stale": doc.stale
                }
                for doc in docs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(e)}")

@app.post("/generate-complete-repo-docs")
def generate_complete_repo_docs(repo_path: str, output_file: str = "Complete_Repository_Documentation.md"):
    """Generate comprehensive documentation for entire repository"""
    try:
        if not os.path.exists(repo_path):
            raise HTTPException(status_code=404, detail=f"Repository not found: {repo_path}")
        
        # Scan repository structure
        structure = repo_scanner.scan_repository(repo_path)
        architecture = repo_scanner.analyze_code_architecture(repo_path)
        structure_tree = repo_scanner.generate_code_structure_tree(repo_path)
        code_files = repo_scanner.get_code_files_for_analysis(repo_path)
        
        # Generate comprehensive documentation
        doc_content = f"""# Complete Repository Documentation

**Repository:** {repo_path}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Repository Overview
- **Total Files:** {structure.get('total_files', 0)}
- **Languages:** {', '.join(structure.get('languages', {}).keys())}
- **Project Type:** {structure.get('package_structure', {}).get('project_type', 'Unknown')}
- **Frameworks:** {', '.join(structure.get('package_structure', {}).get('frameworks', []))}

## Repository Structure
```
{structure_tree}
```

## Architecture Analysis
**Detected Patterns:** {', '.join(architecture.get('patterns', []))}
**Architectural Layers:**
{chr(10).join([f"- **{layer.title()}:** {len(files)} files" for layer, files in architecture.get('layers', {}).items()])}

## File Distribution
{chr(10).join([f"- **{lang.title()}:** {count} files" for lang, count in structure.get('languages', {}).items()])}

## Detailed File Documentation

"""
        
        # Generate docs for key files
        documented_files = 0
        for file_info in code_files[:8]:  # Limit for performance
            try:
                lang_key = file_info["language"].lower()
                if lang_key == "javascript":
                    lang_key = "js"
                elif lang_key == "typescript":
                    lang_key = "ts"
                elif lang_key == "python":
                    lang_key = "py"
                
                parser_class = PARSERS.get(lang_key)
                if parser_class and os.path.exists(file_info["full_path"]):
                    parser = parser_class()
                    functions = parser.parse_file(file_info["full_path"])
                    code_structure = repo_scanner.extract_class_structure(file_info["full_path"], file_info["language"])
                    
                    if functions or code_structure.get('classes'):
                        doc_content += f"### {file_info['file_path']}\\n"
                        doc_content += f"**Language:** {file_info['language'].title()}\\n"
                        doc_content += f"**Type:** {file_info.get('file_type', 'other').title()}\\n\\n"
                        
                        if code_structure.get('classes'):
                            doc_content += "**Classes:**\\n"
                            for cls in code_structure['classes'][:5]:
                                doc_content += f"- `{cls['name']}` (line {cls['line']})\\n"
                                if cls.get('methods'):
                                    for method in cls['methods'][:3]:
                                        doc_content += f"  - `{method['name']}()` (line {method['line']})\\n"
                            doc_content += "\\n"
                        
                        # Generate AI docs for key functions
                        for func in functions[:2]:
                            try:
                                func.commits = []
                                summary = doc_generator.generate_function_doc(func)
                                doc_content += f"#### {func.name}\\n{summary}\\n\\n"
                            except Exception:
                                doc_content += f"#### {func.name}\\n**Parameters:** {', '.join(func.params) if func.params else 'None'}\\n**Lines:** {func.lineno}-{func.end_lineno}\\n\\n"
                        
                        doc_content += "---\\n\\n"
                        documented_files += 1
            except Exception as e:
                print(f"Error processing {file_info['file_path']}: {e}")
                continue
        
        doc_content += f"""
## Summary
- **Total files in repository:** {structure.get('total_files', 0)}
- **Code files analyzed:** {len(code_files)}
- **Files documented:** {documented_files}
- **Languages detected:** {', '.join(structure.get('languages', {}).keys())}

*Generated by Starter Doc Generator*
"""
        
        # Save documentation in organized folder structure
        docs_folder = os.path.join(os.getcwd(), "documentation-generated", "complete")
        os.makedirs(docs_folder, exist_ok=True)
        output_path = os.path.join(docs_folder, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        return {
            "success": True,
            "message": f"Complete repository documentation generated successfully",
            "output_file": output_file,
            "output_path": output_path,
            "output_folder": "documentation-generated/complete/",
            "files_analyzed": len(code_files),
            "files_documented": documented_files,
            "total_files": structure.get('total_files', 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository documentation failed: {str(e)}")

@app.post("/generate-individual-docs")
def generate_individual_docs(repo_path: str, language: str = "java"):
    """Generate separate documentation file for each code file in the repository"""
    try:
        if not os.path.exists(repo_path):
            raise HTTPException(status_code=404, detail=f"Repository not found: {repo_path}")
        
        # Get code files for the specified language
        code_files = repo_scanner.get_code_files_for_analysis(repo_path, [language])
        
        generated_docs = []
        for file_info in code_files:
            try:
                # Map language for parser
                lang_key = file_info["language"].lower()
                if lang_key == "javascript":
                    lang_key = "js"
                elif lang_key == "typescript":
                    lang_key = "ts"
                elif lang_key == "python":
                    lang_key = "py"
                
                parser_class = PARSERS.get(lang_key)
                if not parser_class or not os.path.exists(file_info["full_path"]):
                    continue
                
                # Parse functions
                parser = parser_class()
                functions = parser.parse_file(file_info["full_path"])
                
                if not functions:
                    continue
                
                # Generate documentation content
                file_doc_content = f"""# Documentation for {file_info['file_path']}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Repository: {repo_path}
Language: {file_info['language']}

---

"""
                
                # Generate AI docs for each function
                for func in functions:
                    try:
                        func.commits = []  # Skip git analysis for performance
                        summary = doc_generator.generate_function_doc(func)
                        file_doc_content += f"{summary}\\n\\n---\\n\\n"
                    except Exception:
                        file_doc_content += f"""# {func.name}

## Description
Function '{func.name}' with {len(func.params)} parameter(s)

## Parameters
{chr(10).join([f"- **{param}**: Parameter description needed" for param in func.params]) if func.params else "No parameters"}

## Location
- **File:** {func.file_path}
- **Lines:** {func.lineno}-{func.end_lineno}

---

"""
                
                # Save individual file documentation in organized folder structure
                docs_folder = os.path.join(os.getcwd(), "documentation-generated", "individual")
                os.makedirs(docs_folder, exist_ok=True)
                filename_base = os.path.basename(file_info['file_path']).replace('.', '_')
                doc_filename = f"Individual_{filename_base}_Documentation.md"
                doc_path = os.path.join(docs_folder, doc_filename)
                
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(file_doc_content)
                
                generated_docs.append({
                    "file_path": file_info['file_path'],
                    "documentation_file": doc_filename,
                    "functions_documented": len(functions)
                })
                
            except Exception as e:
                print(f"Error processing {file_info['file_path']}: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Generated individual documentation for {len(generated_docs)} files",
            "repository_path": repo_path,
            "language": language,
            "output_folder": "documentation-generated/individual/",
            "generated_files": generated_docs,
            "total_files_processed": len(generated_docs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Individual documentation generation failed: {str(e)}")

# ===== DOCUMENT CONVERSION ENDPOINTS =====

@app.post("/convert-docs-to-word")
def convert_documentation_to_word(folder_path: str = "documentation-generated"):
    """Convert all markdown documentation files to Word format"""
    try:
        converter = DocumentConverter()
        
        full_folder_path = os.path.join(os.getcwd(), folder_path)
        
        if not os.path.exists(full_folder_path):
            raise HTTPException(status_code=404, detail=f"Documentation folder not found: {full_folder_path}")
        
        # Check what files exist before conversion
        md_files = []
        for root, dirs, files in os.walk(full_folder_path):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
        
        if not md_files:
            return {
                "success": True,
                "message": "No markdown files found to convert",
                "folder_path": full_folder_path,
                "converted_files": [],
                "errors": []
            }
        
        results = converter.convert_documentation_folder(full_folder_path, formats=['docx'])
        
        success_count = len(results['converted'])
        error_count = len(results['errors'])
        
        return {
            "success": True,
            "message": f"Word conversion completed: {success_count} successful, {error_count} errors",
            "folder_path": full_folder_path,
            "converted_files": results['converted'],
            "errors": results['errors'],
            "note": "PDF conversion has been removed - only Word format available"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Word conversion failed: {str(e)}")

@app.post("/convert-single-file")
def convert_single_markdown_file(file_path: str, formats: List[str] = ["docx"]):
    """Convert a single markdown file to Word format only"""
    try:
        converter = DocumentConverter()
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        if not file_path.endswith('.md'):
            raise HTTPException(status_code=400, detail="File must be a markdown (.md) file")
        
        converted_files = []
        errors = []
        
        for format_type in formats:
            try:
                if format_type.lower() in ['docx', 'word']:
                    output_path = converter.convert_to_word(file_path)
                    converted_files.append({
                        'source': file_path,
                        'output': output_path,
                        'format': 'docx'
                    })
                elif format_type.lower() == 'pdf':
                    errors.append({
                        'format': format_type,
                        'error': "PDF conversion not available - feature removed"
                    })
                else:
                    errors.append({
                        'format': format_type,
                        'error': f"Unsupported format: {format_type}. Only 'docx' supported"
                    })
            except Exception as e:
                errors.append({
                    'format': format_type,
                    'error': str(e)
                })
        
        return {
            "success": True,
            "message": f"Converted file to {len(converted_files)} format(s)",
            "source_file": file_path,
            "converted_files": converted_files,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File conversion failed: {str(e)}")

# ===== TESTING ENDPOINTS =====
# ===== TESTING ENDPOINTS =====

@app.get("/test-all")
def test_all_apis():
    """Test all API endpoints with the Employee Management System repository"""
    try:
        # Test parameters for Employee Management System
        test_file = "src/main/java/com/example/EmployeeManagementSystem/model/Employee.java"
        test_repo = r"C:\Users\User\Documents\Clone_GithubProject\Employee-Management-Sys\EmployeeManagementSystem"
        test_language = "java"
        
        results = {}
        
        # 1. Test supported languages
        try:
            results["supported_languages"] = get_supported_languages()
        except Exception as e:
            results["supported_languages"] = {"error": str(e)}
        
        # 2. Test repository structure scan
        try:
            results["repository_scan"] = scan_repository(test_repo)
        except Exception as e:
            results["repository_scan"] = {"error": str(e)}
        
        # 3. Test analyze single file functions
        try:
            results["single_file_analysis"] = analyze_functions(test_file, test_repo, test_language)
        except Exception as e:
            results["single_file_analysis"] = {"error": str(e)}
        
        # 4. Test generate docs for single file
        try:
            results["single_file_docs"] = generate_docs(test_file, test_repo, test_language)
        except Exception as e:
            results["single_file_docs"] = {"error": str(e)}
        
        # 5. Generate complete repository documentation
        try:
            results["complete_repo_docs"] = generate_complete_repo_docs(test_repo, "Complete_Employee_System_Docs.md")
        except Exception as e:
            results["complete_repo_docs"] = {"error": str(e)}
        
        # 6. Generate individual documentation for each Java file
        try:
            results["individual_file_docs"] = generate_individual_docs(test_repo, "java")
        except Exception as e:
            results["individual_file_docs"] = {"error": str(e)}
        
        # 7. Test document conversion to Word
        try:
            results["word_conversion"] = convert_documentation_to_word("documentation-generated")
        except Exception as e:
            results["word_conversion"] = {"error": str(e)}
        
        # 8. Test single file conversion (if documentation files exist)
        try:
            doc_files = []
            for root, dirs, files in os.walk("documentation-generated"):
                for file in files:
                    if file.endswith('.md'):
                        doc_files.append(os.path.join(root, file))
                        break  # Just test one file
                if doc_files:
                    break
            
            if doc_files:
                test_md_file = doc_files[0]
                results["single_file_conversion"] = convert_single_markdown_file(test_md_file, ["docx"])
            else:
                results["single_file_conversion"] = {"message": "No markdown files found for testing"}
        except Exception as e:
            results["single_file_conversion"] = {"error": str(e)}
        
        return {
            "success": True,
            "message": "All API tests completed - Word conversion only",
            "test_repository": test_repo,
            "test_file": test_file,
            "test_language": test_language,
            "results": results,
            "summary": {
                "total_tests": 8,
                "successful_tests": len([r for r in results.values() if not isinstance(r, dict) or "error" not in r]),
                "failed_tests": len([r for r in results.values() if isinstance(r, dict) and "error" in r]),
                "conversion_tests": {
                    "word_conversion": "success" if "error" not in results.get("word_conversion", {}) else "failed",
                    "single_file": "success" if "error" not in results.get("single_file_conversion", {}) else "failed",
                    "note": "PDF conversion removed - only Word format available"
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Test execution failed: {str(e)}",
            "message": "Critical error during API testing"
        }

# ===== SERVER STARTUP =====

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
