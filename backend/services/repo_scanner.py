"""
Repository structure scanner for comprehensive codebase analysis
"""
import os
from typing import Dict, List, Any
from pathlib import Path
import json

class RepoScanner:
    def extract_class_relationships(self, repo_path: str, language: str = "java") -> dict:
        """
        Extract class relationships, attributes, and method signatures for visualization.
        Returns: { 'classes': {name: {'parents': [...], 'associations': [...], 'attributes': [...], 'methods': [...]}} }
        """
        import re
        relationships = {"classes": {}}
        class_names = set()
        # First pass: collect all class names
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if language == "java" and file.endswith(".java"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        class_matches = re.findall(r'class\s+(\w+)', content)
                        for cname in class_matches:
                            class_names.add(cname)
                    except Exception:
                        continue
        # Second pass: extract relationships and details
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if language == "java" and file.endswith(".java"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Find class declarations
                        class_decl = re.findall(r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w, ]+))?', content)
                        for match in class_decl:
                            class_name = match[0]
                            parent = match[1] if match[1] else None
                            implements = [i.strip() for i in match[2].split(',')] if match[2] else []
                            if class_name not in relationships["classes"]:
                                relationships["classes"][class_name] = {"parents": [], "associations": [], "attributes": [], "methods": []}
                            if parent:
                                relationships["classes"][class_name]["parents"].append(parent)
                            for impl in implements:
                                relationships["classes"][class_name]["parents"].append(impl)
                        # Find attributes (fields)
                        attr_matches = re.findall(r'(public|private|protected)?\s*([\w<>\[\]]+)\s+(\w+)\s*;', content)
                        for _, attr_type, attr_name in attr_matches:
                            relationships["classes"][class_name]["attributes"].append(f"{attr_type} {attr_name}")
                            if attr_type in class_names and attr_type != class_name:
                                relationships["classes"][class_name]["associations"].append(attr_type)
                        # Find method signatures and parameter associations
                        method_matches = re.findall(r'(public|private|protected)?\s*([\w<>\[\]]+)\s+(\w+)\s*\(([^)]*)\)', content)
                        for _, ret_type, method_name, params in method_matches:
                            param_types = [p.strip().split()[0] for p in params.split(',') if p.strip()]
                            param_str = ', '.join([p.strip() for p in params.split(',') if p.strip()])
                            relationships["classes"][class_name]["methods"].append(f"{ret_type} {method_name}({param_str})")
                            for ptype in param_types:
                                if ptype in class_names and ptype != class_name:
                                    relationships["classes"][class_name]["associations"].append(ptype)
                    except Exception:
                        continue
        # Remove duplicate associations and attributes
        for cls in relationships["classes"]:
            relationships["classes"][cls]["associations"] = list(set(relationships["classes"][cls]["associations"]))
            relationships["classes"][cls]["attributes"] = list(set(relationships["classes"][cls]["attributes"]))
        return relationships

    def generate_mermaid_class_diagram(self, relationships: dict) -> str:
        """
        Generate a detailed Mermaid class diagram from relationships dict.
        """
        lines = ["classDiagram"]
        for cls, info in relationships.get('classes', {}).items():
            for parent in info.get('parents', []):
                lines.append(f"{parent} <|-- {cls}")
            for assoc in info.get('associations', []):
                lines.append(f"{cls} --> {assoc}")
            # Add class block with attributes and methods
            lines.append(f"class {cls} {{")
            for attr in info.get('attributes', []):
                lines.append(f"  {attr}")
            for method in info.get('methods', []):
                lines.append(f"  {method}")
            lines.append("}")
        return "\n".join(lines)
    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.md': 'markdown',
            '.txt': 'text',
            '.json': 'json',
            '.xml': 'xml',
            '.yml': 'yaml',
            '.yaml': 'yaml'
        }
        def extract_class_relationships(self, repo_path: str, language: str = "java") -> dict:
            """
            Extract class relationships (inheritance, associations) for visualization.
            Returns: { 'classes': {name: {'parents': [...], 'associations': [...]}} }
            """
            import re
            relationships = {"classes": {}}
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if language == "java" and file.endswith(".java"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            # Find class declarations
                            class_matches = re.findall(r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w, ]+))?', content)
                            for match in class_matches:
                                class_name = match[0]
                                parent = match[1] if match[1] else None
                                implements = [i.strip() for i in match[2].split(',')] if match[2] else []
                                if class_name not in relationships["classes"]:
                                    relationships["classes"][class_name] = {"parents": [], "associations": []}
                                if parent:
                                    relationships["classes"][class_name]["parents"].append(parent)
                                for impl in implements:
                                    relationships["classes"][class_name]["parents"].append(impl)
                            # Find associations (fields of other class types)
                            field_matches = re.findall(r'(\w+)\s+(\w+);', content)
                            for type_name, var_name in field_matches:
                                # Only associate with known classes
                                if type_name in relationships["classes"] and type_name != class_name:
                                    relationships["classes"][class_name]["associations"].append(type_name)
                        except Exception:
                            continue
                    # Add support for other languages here if needed
            return relationships

        def generate_mermaid_class_diagram(self, relationships: dict) -> str:
            """
            Generate a Mermaid class diagram from relationships dict.
            """
            lines = ["```mermaid", "classDiagram"]
            for cls, info in relationships.get('classes', {}).items():
                for parent in info.get('parents', []):
                    lines.append(f"{parent} <|-- {cls}")
                for assoc in info.get('associations', []):
                    lines.append(f"{cls} --> {assoc}")
                lines.append(f"class {cls}")
            lines.append("```")
            return "\n".join(lines)
    
    def scan_repository(self, repo_path: str) -> Dict[str, Any]:
        """Scan entire repository and return structure analysis"""
        try:
            repo_structure = {
                "repository_path": repo_path,
                "total_files": 0,
                "languages": {},
                "directories": [],
                "file_tree": {},
                "code_files": [],
                "documentation_files": [],
                "config_files": [],
                "test_files": [],
                "main_files": [],
                "package_structure": {}
            }
            
            # Walk through all directories
            for root, dirs, files in os.walk(repo_path):
                # Skip common ignored directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'target', '__pycache__', 'venv', 'env']]
                
                relative_path = os.path.relpath(root, repo_path)
                if relative_path != '.':
                    repo_structure["directories"].append(relative_path)
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(file_path, repo_path)
                    
                    repo_structure["total_files"] += 1
                    
                    # Analyze file type
                    file_ext = Path(file).suffix.lower()
                    if file_ext in self.supported_extensions:
                        lang = self.supported_extensions[file_ext]
                        repo_structure["languages"][lang] = repo_structure["languages"].get(lang, 0) + 1
                        
                        # Categorize files
                        self._categorize_file(file, relative_file_path, repo_structure)
            
            # Analyze package/project structure
            repo_structure["package_structure"] = self._analyze_package_structure(repo_path)
            
            return repo_structure
            
        except Exception as e:
            return {"error": f"Failed to scan repository: {str(e)}"}
    
    def _categorize_file(self, filename: str, relative_path: str, structure: Dict):
        """Categorize files by their purpose"""
        filename_lower = filename.lower()
        
        # Code files
        if any(filename.endswith(ext) for ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.java']):
            structure["code_files"].append({
                "path": relative_path,
                "name": filename,
                "type": self._get_file_purpose(filename_lower, relative_path)
            })
        
        # Documentation files
        elif any(filename.endswith(ext) for ext in ['.md', '.txt', '.rst']):
            structure["documentation_files"].append(relative_path)
        
        # Configuration files
        elif any(name in filename_lower for name in ['config', 'setting', 'properties', 'pom.xml', 'package.json', 'requirements.txt']):
            structure["config_files"].append(relative_path)
        
        # Test files
        elif any(name in filename_lower for name in ['test', 'spec']):
            structure["test_files"].append(relative_path)
        
        # Main/entry files
        elif any(name in filename_lower for name in ['main', 'app', 'index', 'application']):
            structure["main_files"].append(relative_path)
    
    def _get_file_purpose(self, filename: str, relative_path: str) -> str:
        """Determine the purpose of a code file"""
        path_lower = relative_path.lower()
        
        if 'controller' in path_lower or 'controller' in filename:
            return 'controller'
        elif 'service' in path_lower or 'service' in filename:
            return 'service'
        elif 'model' in path_lower or 'entity' in path_lower or 'dto' in path_lower:
            return 'model'
        elif 'repository' in path_lower or 'dao' in path_lower:
            return 'repository'
        elif 'util' in path_lower or 'helper' in path_lower:
            return 'utility'
        elif 'test' in path_lower or 'spec' in filename:
            return 'test'
        elif 'config' in path_lower or 'setting' in filename:
            return 'configuration'
        elif 'main' in filename or 'app' in filename or 'application' in filename:
            return 'main'
        else:
            return 'other'
    
    def _analyze_package_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze project structure and dependencies"""
        structure = {
            "project_type": "unknown",
            "main_language": "unknown",
            "frameworks": [],
            "dependencies": {},
            "entry_points": []
        }
        
        # Check for common project files
        project_files = {
            'pom.xml': 'maven_java',
            'build.gradle': 'gradle_java',
            'package.json': 'node_js',
            'requirements.txt': 'python',
            'setup.py': 'python',
            'Cargo.toml': 'rust',
            'go.mod': 'go'
        }
        
        for file, project_type in project_files.items():
            file_path = os.path.join(repo_path, file)
            if os.path.exists(file_path):
                structure["project_type"] = project_type
                structure["main_language"] = project_type.split('_')[-1] if '_' in project_type else project_type
                
                # Read dependencies
                try:
                    if file == 'package.json':
                        with open(file_path, 'r') as f:
                            package_data = json.load(f)
                            structure["dependencies"] = package_data.get('dependencies', {})
                            structure["frameworks"] = self._detect_js_frameworks(package_data)
                    elif file == 'requirements.txt':
                        with open(file_path, 'r') as f:
                            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                            structure["dependencies"] = {dep.split('==')[0] if '==' in dep else dep: '' for dep in deps}
                            structure["frameworks"] = self._detect_python_frameworks(deps)
                except Exception:
                    pass
                break
        
        return structure
    
    def _detect_js_frameworks(self, package_data: Dict) -> List[str]:
        """Detect JavaScript frameworks from package.json"""
        frameworks = []
        dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
        
        framework_indicators = {
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'express': 'Express.js',
            'next': 'Next.js',
            'nuxt': 'Nuxt.js',
            'svelte': 'Svelte'
        }
        
        for dep in dependencies:
            for indicator, framework in framework_indicators.items():
                if indicator in dep.lower():
                    frameworks.append(framework)
                    break
        
        return list(set(frameworks))
    
    def _detect_python_frameworks(self, dependencies: List[str]) -> List[str]:
        """Detect Python frameworks from requirements"""
        frameworks = []
        
        framework_indicators = {
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'tornado': 'Tornado',
            'pyramid': 'Pyramid',
            'bottle': 'Bottle'
        }
        
        for dep in dependencies:
            dep_lower = dep.lower()
            for indicator, framework in framework_indicators.items():
                if indicator in dep_lower:
                    frameworks.append(framework)
                    break
        
        return list(set(frameworks))
    
    def get_code_files_for_analysis(self, repo_path: str, file_types: List[str] = None) -> List[Dict[str, str]]:
        """Get list of code files ready for documentation analysis"""
        if file_types is None:
            file_types = ['python', 'javascript', 'typescript', 'java']
        
        files_for_analysis = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'target', '__pycache__', 'venv', 'env']]
            
            for file in files:
                file_ext = Path(file).suffix.lower()
                if file_ext in self.supported_extensions:
                    lang = self.supported_extensions[file_ext]
                    if lang in file_types:
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, repo_path)
                        
                        files_for_analysis.append({
                            "file_path": relative_path,
                            "full_path": full_path,
                            "language": lang,
                            "file_type": self._get_file_purpose(file.lower(), relative_path)
                        })
        
        return files_for_analysis
    
    def generate_code_structure_tree(self, repo_path: str) -> str:
        """Generate a visual tree structure of the codebase"""
        try:
            structure_lines = []
            structure_lines.append("```")
            structure_lines.append(f"{os.path.basename(repo_path)}/")
            
            # Get all files and directories
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden and build directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'target', '__pycache__', 'venv', 'env', 'bin', 'obj']]
                
                level = root.replace(repo_path, '').count(os.sep)
                indent = '  ' * level
                subindent = '  ' * (level + 1)
                
                if level > 0:  # Don't show root again
                    relative_path = os.path.relpath(root, repo_path)
                    structure_lines.append(f"{indent}├── {os.path.basename(root)}/")
                
                # Show files in this directory
                for file in files[:10]:  # Limit files shown per directory
                    if not file.startswith('.'):
                        file_ext = Path(file).suffix.lower()
                        if file_ext in self.supported_extensions or file in ['README.md', 'pom.xml', 'package.json', 'requirements.txt']:
                            structure_lines.append(f"{subindent}├── {file}")
                
                if len(files) > 10:
                    structure_lines.append(f"{subindent}└── ... ({len(files) - 10} more files)")
                
                # Limit depth to avoid massive output
                if level > 3:
                    break
            
            structure_lines.append("```")
            return "\n".join(structure_lines)
        except Exception as e:
            return f"Error generating structure tree: {str(e)}"
    
    def analyze_code_architecture(self, repo_path: str) -> Dict[str, Any]:
        """Analyze the overall code architecture and patterns"""
        architecture = {
            "layers": {},
            "patterns": [],
            "dependencies": {},
            "entry_points": [],
            "data_flow": {}
        }
        
        try:
            # Analyze by file types and locations
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'target', '__pycache__', 'venv', 'env']]
                
                relative_path = os.path.relpath(root, repo_path)
                layer_name = self._identify_architectural_layer(relative_path)
                
                if layer_name != "unknown":
                    if layer_name not in architecture["layers"]:
                        architecture["layers"][layer_name] = []
                    
                    for file in files:
                        if any(file.endswith(ext) for ext in ['.py', '.js', '.java', '.ts']):
                            architecture["layers"][layer_name].append({
                                "file": file,
                                "path": relative_path
                            })
            
            # Detect architectural patterns
            if "controller" in architecture["layers"] or "service" in architecture["layers"]:
                architecture["patterns"].append("MVC/Layered Architecture")
            if "model" in architecture["layers"] and "repository" in architecture["layers"]:
                architecture["patterns"].append("Repository Pattern")
            if "dto" in architecture["layers"]:
                architecture["patterns"].append("Data Transfer Object Pattern")
            
            return architecture
        except Exception as e:
            return {"error": f"Architecture analysis failed: {str(e)}"}
    
    def _identify_architectural_layer(self, path: str) -> str:
        """Identify which architectural layer a path belongs to"""
        path_lower = path.lower()
        
        if 'controller' in path_lower:
            return "controller"
        elif 'service' in path_lower:
            return "service"
        elif 'model' in path_lower or 'entity' in path_lower:
            return "model"
        elif 'repository' in path_lower or 'dao' in path_lower:
            return "repository"
        elif 'dto' in path_lower:
            return "dto"
        elif 'config' in path_lower:
            return "configuration"
        elif 'util' in path_lower or 'helper' in path_lower:
            return "utility"
        elif 'test' in path_lower:
            return "test"
        else:
            return "unknown"
    
    def extract_class_structure(self, file_path: str, language: str) -> Dict[str, Any]:
        """Extract class and method structure from a code file"""
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "constants": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if language == 'java':
                structure = self._extract_java_structure(content)
            elif language in ['python', 'py']:
                structure = self._extract_python_structure(content)
            elif language in ['javascript', 'js', 'typescript', 'ts']:
                structure = self._extract_js_structure(content)
                
        except Exception as e:
            structure["error"] = str(e)
        
        return structure
    
    def _extract_java_structure(self, content: str) -> Dict[str, Any]:
        """Extract Java class structure"""
        structure = {"classes": [], "functions": [], "imports": [], "constants": []}
        
        lines = content.split('\n')
        current_class = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Extract imports
            if line.startswith('import '):
                structure["imports"].append(line.replace('import ', '').replace(';', ''))
            
            # Extract class declarations
            if 'class ' in line and '{' in line:
                class_match = line.split('class ')[1].split('{')[0].strip()
                current_class = {
                    "name": class_match.split()[0],
                    "line": i + 1,
                    "methods": [],
                    "attributes": []
                }
                structure["classes"].append(current_class)
            
            # Extract methods
            if current_class and ('public ' in line or 'private ' in line or 'protected ' in line) and '(' in line and ')' in line:
                if 'class ' not in line:  # Not a class declaration
                    method_name = self._extract_method_name_java(line)
                    if method_name:
                        current_class["methods"].append({
                            "name": method_name,
                            "line": i + 1,
                            "signature": line.strip()
                        })
        
        return structure
    
    def _extract_python_structure(self, content: str) -> Dict[str, Any]:
        """Extract Python class and function structure"""
        structure = {"classes": [], "functions": [], "imports": [], "constants": []}
        
        lines = content.split('\n')
        current_class = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Extract imports
            if stripped.startswith('import ') or stripped.startswith('from '):
                structure["imports"].append(stripped)
            
            # Extract class declarations
            if stripped.startswith('class '):
                class_name = stripped.split('class ')[1].split('(')[0].split(':')[0].strip()
                current_class = {
                    "name": class_name,
                    "line": i + 1,
                    "methods": [],
                    "attributes": []
                }
                structure["classes"].append(current_class)
            
            # Extract function/method declarations
            if stripped.startswith('def '):
                func_name = stripped.split('def ')[1].split('(')[0].strip()
                func_info = {
                    "name": func_name,
                    "line": i + 1,
                    "signature": stripped
                }
                
                if current_class:
                    current_class["methods"].append(func_info)
                else:
                    structure["functions"].append(func_info)
        
        return structure
    
    def _extract_js_structure(self, content: str) -> Dict[str, Any]:
        """Extract JavaScript/TypeScript structure"""
        structure = {"classes": [], "functions": [], "imports": [], "constants": []}
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Extract imports
            if stripped.startswith('import ') or stripped.startswith('const ') and 'require(' in stripped:
                structure["imports"].append(stripped)
            
            # Extract class declarations
            if stripped.startswith('class '):
                class_name = stripped.split('class ')[1].split('{')[0].split('extends')[0].strip()
                structure["classes"].append({
                    "name": class_name,
                    "line": i + 1,
                    "methods": []
                })
            
            # Extract function declarations
            if stripped.startswith('function ') or 'function(' in stripped:
                func_name = self._extract_function_name_js(stripped)
                if func_name:
                    structure["functions"].append({
                        "name": func_name,
                        "line": i + 1,
                        "signature": stripped
                    })
        
        return structure
    
    def _extract_method_name_java(self, line: str) -> str:
        """Extract method name from Java method declaration"""
        try:
            # Remove access modifiers and return type
            parts = line.replace('public', '').replace('private', '').replace('protected', '').replace('static', '').strip()
            # Find method name (word before opening parenthesis)
            if '(' in parts:
                before_paren = parts.split('(')[0].strip()
                method_name = before_paren.split()[-1]
                return method_name
        except:
            pass
        return None
    
    def _extract_function_name_js(self, line: str) -> str:
        """Extract function name from JavaScript function declaration"""
        try:
            if 'function ' in line:
                after_function = line.split('function ')[1]
                func_name = after_function.split('(')[0].strip()
                return func_name
        except:
            pass
        return None
