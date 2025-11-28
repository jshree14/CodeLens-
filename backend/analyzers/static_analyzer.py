import ast
import tempfile
import os
import subprocess
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class StaticAnalyzer:
    """
    Comprehensive static code analyzer
    Performs syntax checking, complexity analysis, and code quality metrics
    """
    
    def __init__(self):
        self.supported_languages = [
            'python', 'javascript', 'typescript', 'java', 'cpp', 'c', 
            'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'
        ]
        logger.info(f"Static Analyzer initialized for languages: {self.supported_languages}")
    
    async def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """
        Comprehensive static analysis of code
        Returns detailed metrics, issues, and quality assessment
        """
        try:
            logger.info(f"Starting static analysis for {language} code ({len(code)} characters)")
            
            if language == 'python':
                return await self._analyze_python(code)
            elif language in ['javascript', 'typescript']:
                return await self._analyze_javascript(code, language)
            elif language == 'java':
                return await self._analyze_java(code)
            elif language in ['cpp', 'c']:
                return await self._analyze_cpp(code)
            else:
                return await self._analyze_generic(code, language)
                
        except Exception as e:
            logger.error(f"Static analysis failed for {language}: {e}")
            return self._create_error_result(str(e), code, language)
    
    async def _analyze_python(self, code: str) -> Dict[str, Any]:
        """
        Comprehensive Python code analysis using AST, pylint, and custom checks
        """
        results = {
            "issues": [],
            "metrics": {},
            "quality_indicators": {},
            "complexity_analysis": {}
        }
        
        try:
            # Parse AST for comprehensive metrics
            tree = ast.parse(code)
            results["metrics"] = self._extract_python_metrics(tree, code)
            results["complexity_analysis"] = self._analyze_python_complexity(tree)
            results["quality_indicators"] = self._analyze_python_quality(tree, code)
            
            # Check for syntax and structural issues
            syntax_issues = self._check_python_syntax_issues(tree, code)
            results["issues"].extend(syntax_issues)
            
            # Check for code style issues
            style_issues = self._check_python_style_issues(code)
            results["issues"].extend(style_issues)
            
            # Check for potential bugs
            bug_issues = self._check_python_potential_bugs(tree, code)
            results["issues"].extend(bug_issues)
            
            # Run pylint for additional issues (if available)
            pylint_issues = await self._run_pylint(code)
            results["issues"].extend(pylint_issues)
            
            logger.info(f"Python analysis completed: {len(results['issues'])} issues found")
            
        except SyntaxError as e:
            results["issues"].append({
                "title": "Syntax Error",
                "description": f"Python syntax error at line {e.lineno}: {str(e)}",
                "severity": "error",
                "suggestion": "Fix the syntax error before proceeding",
                "line_number": e.lineno if hasattr(e, 'lineno') else None
            })
        except Exception as e:
            logger.error(f"Python analysis error: {e}")
            results["issues"].append({
                "title": "Analysis Error",
                "description": f"Failed to analyze Python code: {str(e)}",
                "severity": "warning",
                "suggestion": "Check code structure and try again"
            })
        
        return results
    
    def _extract_python_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Extract comprehensive metrics from Python AST"""
        lines = code.split('\n')
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "functions": 0,
            "classes": 0,
            "methods": 0,
            "loops": 0,
            "conditions": 0,
            "try_blocks": 0,
            "imports": 0,
            "variables": 0,
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
        }
        
        # Walk through AST nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'parent') and isinstance(node.parent, ast.ClassDef):
                    metrics["methods"] += 1
                else:
                    metrics["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
            elif isinstance(node, (ast.For, ast.While)):
                metrics["loops"] += 1
            elif isinstance(node, ast.If):
                metrics["conditions"] += 1
            elif isinstance(node, ast.Try):
                metrics["try_blocks"] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics["imports"] += 1
            elif isinstance(node, ast.Assign):
                metrics["variables"] += len(node.targets)
        
        return metrics
    
    def _analyze_python_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze code complexity metrics"""
        complexity_data = {
            "cyclomatic_complexity": 1,  # Base complexity
            "nesting_depth": 0,
            "function_complexities": [],
            "class_complexities": []
        }
        
        # Calculate cyclomatic complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity_data["cyclomatic_complexity"] += 1
            elif isinstance(node, ast.BoolOp):
                complexity_data["cyclomatic_complexity"] += len(node.values) - 1
        
        # Analyze function complexities
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_complexity = self._calculate_function_complexity(node)
                complexity_data["function_complexities"].append({
                    "name": node.name,
                    "complexity": func_complexity,
                    "line_number": node.lineno
                })
        
        # Calculate maximum nesting depth
        complexity_data["nesting_depth"] = self._calculate_max_nesting_depth(tree)
        
        return complexity_data
    
    def _analyze_python_quality(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Analyze code quality indicators"""
        quality = {
            "has_docstrings": False,
            "has_type_hints": False,
            "has_error_handling": False,
            "follows_naming_conventions": True,
            "documentation_ratio": 0.0,
            "test_coverage_indicators": []
        }
        
        # Check for docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    quality["has_docstrings"] = True
                    break
        
        # Check for type hints
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    quality["has_type_hints"] = True
                    break
        
        # Check for error handling
        for node in ast.walk(tree):
            if isinstance(node, (ast.Try, ast.ExceptHandler)):
                quality["has_error_handling"] = True
                break
        
        # Calculate documentation ratio
        lines = code.split('\n')
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        if code_lines > 0:
            quality["documentation_ratio"] = comment_lines / code_lines
        
        return quality
    
    async def _run_pylint(self, code: str) -> List[Dict[str, Any]]:
        """Run pylint on Python code"""
        issues = []
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run pylint
            result = subprocess.run(
                ['pylint', '--output-format=json', '--disable=C0114,C0115,C0116', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                pylint_output = json.loads(result.stdout)
                for item in pylint_output[:10]:  # Limit to 10 issues
                    severity = "error" if item.get("type") == "error" else "warning"
                    issues.append({
                        "title": item.get("message-id", "Pylint Issue"),
                        "description": item.get("message", ""),
                        "severity": severity,
                        "suggestion": self._get_pylint_suggestion(item.get("message-id", ""))
                    })
            
            os.unlink(temp_file)
            
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # Pylint not available or failed, skip
            pass
        except Exception:
            # Any other error, skip pylint analysis
            pass
        
        return issues
    
    def _get_pylint_suggestion(self, message_id: str) -> str:
        """Get suggestion for pylint message"""
        suggestions = {
            "C0103": "Use snake_case for variable names",
            "W0613": "Remove unused parameters or prefix with underscore",
            "R0903": "Consider adding more methods or combining with other classes",
            "R0913": "Reduce number of parameters or use a configuration object"
        }
        return suggestions.get(message_id, "Follow Python PEP 8 style guidelines")
    
    async def _analyze_javascript(self, code: str, language: str = 'javascript') -> Dict[str, Any]:
        """
        Comprehensive JavaScript/TypeScript analysis
        """
        results = {
            "issues": [],
            "metrics": {},
            "quality_indicators": {},
            "complexity_analysis": {}
        }
        
        try:
            # Extract comprehensive metrics
            results["metrics"] = self._extract_js_metrics(code)
            results["complexity_analysis"] = self._analyze_js_complexity(code)
            results["quality_indicators"] = self._analyze_js_quality(code, language)
            
            # Check for various issues
            syntax_issues = self._check_js_syntax_issues(code)
            results["issues"].extend(syntax_issues)
            
            style_issues = self._check_js_style_issues(code)
            results["issues"].extend(style_issues)
            
            security_issues = self._check_js_security_issues(code)
            results["issues"].extend(security_issues)
            
            performance_issues = self._check_js_performance_issues(code)
            results["issues"].extend(performance_issues)
            
            logger.info(f"JavaScript analysis completed: {len(results['issues'])} issues found")
            
        except Exception as e:
            logger.error(f"JavaScript analysis error: {e}")
            results["issues"].append({
                "title": "Analysis Error",
                "description": f"Failed to analyze JavaScript code: {str(e)}",
                "severity": "warning",
                "suggestion": "Check code structure and try again"
            })
        
        return results
    
    def _extract_js_metrics(self, code: str) -> Dict[str, Any]:
        """Extract comprehensive metrics from JavaScript/TypeScript code"""
        lines = code.split('\n')
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('//')]) + 
                           len(re.findall(r'/\*.*?\*/', code, re.DOTALL)),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "functions": len(re.findall(r'function\s+\w+|=>\s*{|\w+\s*:\s*function|const\s+\w+\s*=\s*\(', code)),
            "arrow_functions": len(re.findall(r'=>', code)),
            "classes": len(re.findall(r'class\s+\w+', code)),
            "methods": len(re.findall(r'\w+\s*\([^)]*\)\s*{', code)),
            "loops": len(re.findall(r'\b(for|while)\s*\(', code)),
            "conditions": len(re.findall(r'\bif\s*\(', code)),
            "try_blocks": len(re.findall(r'\btry\s*{', code)),
            "imports": len(re.findall(r'import\s+.*from|require\s*\(', code)),
            "exports": len(re.findall(r'export\s+|module\.exports', code)),
            "variables": len(re.findall(r'\b(var|let|const)\s+\w+', code)),
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
        }
        
        return metrics
    
    def _analyze_js_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript code complexity"""
        complexity_data = {
            "cyclomatic_complexity": 1,
            "nesting_depth": 0,
            "function_count": 0,
            "callback_depth": 0
        }
        
        # Calculate cyclomatic complexity
        complexity_keywords = re.findall(r'\b(if|for|while|case|catch|\?|&&|\|\|)\b', code)
        complexity_data["cyclomatic_complexity"] += len(complexity_keywords)
        
        # Estimate nesting depth by counting braces
        max_depth = 0
        current_depth = 0
        for char in code:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        complexity_data["nesting_depth"] = max_depth
        complexity_data["function_count"] = len(re.findall(r'function|=>', code))
        
        # Estimate callback depth
        callback_patterns = re.findall(r'\.then\(|\.catch\(|callback\(', code)
        complexity_data["callback_depth"] = len(callback_patterns)
        
        return complexity_data
    
    def _analyze_js_quality(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code quality"""
        quality = {
            "uses_strict_mode": "'use strict'" in code or '"use strict"' in code,
            "has_error_handling": bool(re.search(r'\btry\s*{|\bcatch\s*\(', code)),
            "uses_modern_syntax": bool(re.search(r'\b(const|let|=>|async|await)\b', code)),
            "has_type_annotations": language == 'typescript' and bool(re.search(r':\s*\w+\s*[=;,)]', code)),
            "documentation_ratio": 0.0,
            "uses_semicolons": code.count(';') > 0
        }
        
        # Calculate documentation ratio
        lines = code.split('\n')
        comment_lines = len([line for line in lines if line.strip().startswith('//')])
        comment_lines += len(re.findall(r'/\*.*?\*/', code, re.DOTALL))
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        if code_lines > 0:
            quality["documentation_ratio"] = comment_lines / code_lines
        
        return quality
    
    def _check_js_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Check for common JavaScript issues"""
        issues = []
        
        # Check for var usage
        if 'var ' in code:
            issues.append({
                "title": "Use of 'var' keyword",
                "description": "Found usage of 'var' which has function scope",
                "severity": "warning",
                "suggestion": "Use 'let' or 'const' instead of 'var' for block scope"
            })
        
        # Check for == usage
        if re.search(r'[^=!]==[^=]', code):
            issues.append({
                "title": "Loose equality comparison",
                "description": "Found usage of '==' which can cause type coercion issues",
                "severity": "warning",
                "suggestion": "Use '===' for strict equality comparison"
            })
        
        # Check for console.log
        if 'console.log' in code:
            issues.append({
                "title": "Console statements found",
                "description": "Console.log statements should be removed in production",
                "severity": "info",
                "suggestion": "Remove console.log statements or use a proper logging library"
            })
        
        return issues
    
    async def _analyze_generic(self, code: str, language: str) -> Dict[str, Any]:
        """Generic analysis for unsupported languages"""
        lines = code.split('\n')
        
        return {
            "issues": [{
                "title": f"Limited analysis for {language}",
                "description": f"Full static analysis not available for {language}",
                "severity": "info",
                "suggestion": "Consider using language-specific tools for detailed analysis"
            }],
            "metrics": {
                "lines": len(lines),
                "functions": len(re.findall(r'\w+\s*\([^)]*\)\s*{', code)),
                "complexity": 1 + len(re.findall(r'\b(if|for|while|switch)\b', code))
            }
        }
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a specific function"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_max_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth in the code"""
        def get_depth(node, current_depth=0):
            max_depth = current_depth
            
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                current_depth += 1
            
            for child in ast.iter_child_nodes(node):
                child_depth = get_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        return get_depth(tree)
    
    def _check_python_syntax_issues(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Check for Python syntax and structural issues"""
        issues = []
        
        # Check for unused imports
        imports = []
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
        
        unused_imports = [imp for imp in imports if imp not in used_names]
        if unused_imports:
            issues.append({
                "title": "Unused Imports",
                "description": f"Found unused imports: {', '.join(unused_imports)}",
                "severity": "warning",
                "suggestion": "Remove unused import statements to clean up the code"
            })
        
        return issues
    
    def _check_python_style_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for Python style issues (PEP 8)"""
        issues = []
        lines = code.split('\n')
        
        # Check line length
        long_lines = [(i+1, line) for i, line in enumerate(lines) if len(line) > 79]
        if long_lines:
            issues.append({
                "title": "Long Lines",
                "description": f"Found {len(long_lines)} lines longer than 79 characters",
                "severity": "info",
                "suggestion": "Break long lines to improve readability (PEP 8)",
                "line_number": long_lines[0][0]
            })
        
        # Check for missing blank lines around functions/classes
        for i, line in enumerate(lines):
            if line.strip().startswith(('def ', 'class ')):
                if i > 0 and lines[i-1].strip() and not lines[i-1].strip().startswith('#'):
                    issues.append({
                        "title": "Missing Blank Line",
                        "description": "Missing blank line before function/class definition",
                        "severity": "info",
                        "suggestion": "Add blank lines around top-level function and class definitions",
                        "line_number": i+1
                    })
        
        return issues
    
    def _check_python_potential_bugs(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Check for potential bugs in Python code"""
        issues = []
        
        # Check for mutable default arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "title": "Mutable Default Argument",
                            "description": f"Function '{node.name}' has mutable default argument",
                            "severity": "warning",
                            "suggestion": "Use None as default and create mutable object inside function",
                            "line_number": node.lineno
                        })
        
        # Check for bare except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append({
                    "title": "Bare Except Clause",
                    "description": "Using bare 'except:' can catch system exit exceptions",
                    "severity": "warning",
                    "suggestion": "Specify exception types or use 'except Exception:'",
                    "line_number": node.lineno
                })
        
        return issues
    
    def _check_js_syntax_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for JavaScript syntax and structural issues"""
        issues = []
        
        # Check for missing semicolons (basic check)
        lines = code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped and not stripped.endswith((';', '{', '}', ')', ',')) and 
                not stripped.startswith(('if', 'for', 'while', 'function', 'class', '//', '/*', 'import', 'export')) and
                not stripped.endswith('\\') and '=' in stripped):
                issues.append({
                    "title": "Missing Semicolon",
                    "description": f"Line {i+1} may be missing a semicolon",
                    "severity": "info",
                    "suggestion": "Add semicolons to improve code clarity and avoid ASI issues",
                    "line_number": i+1
                })
                break  # Only report first occurrence
        
        # Check for undefined variables (basic check)
        declared_vars = set(re.findall(r'\b(?:var|let|const)\s+(\w+)', code))
        used_vars = set(re.findall(r'\b(\w+)\s*[=\(\[]', code))
        potentially_undefined = used_vars - declared_vars - {'console', 'document', 'window', 'require', 'module', 'exports'}
        
        if potentially_undefined:
            issues.append({
                "title": "Potentially Undefined Variables",
                "description": f"Variables may be used before declaration: {', '.join(list(potentially_undefined)[:3])}",
                "severity": "warning",
                "suggestion": "Ensure all variables are properly declared before use"
            })
        
        return issues
    
    def _check_js_style_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for JavaScript style issues"""
        issues = []
        
        # Check for var usage
        if 'var ' in code:
            issues.append({
                "title": "Use of 'var' keyword",
                "description": "Found usage of 'var' which has function scope",
                "severity": "warning",
                "suggestion": "Use 'let' or 'const' instead of 'var' for block scope"
            })
        
        # Check for == usage
        if re.search(r'[^=!]==[^=]', code):
            issues.append({
                "title": "Loose Equality Comparison",
                "description": "Found usage of '==' which can cause type coercion issues",
                "severity": "warning",
                "suggestion": "Use '===' for strict equality comparison"
            })
        
        # Check for console.log in production code
        console_count = len(re.findall(r'console\.(log|warn|error)', code))
        if console_count > 2:
            issues.append({
                "title": "Multiple Console Statements",
                "description": f"Found {console_count} console statements",
                "severity": "info",
                "suggestion": "Remove console statements or use a proper logging library"
            })
        
        return issues
    
    def _check_js_security_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for JavaScript security issues"""
        issues = []
        
        # Check for eval usage
        if 'eval(' in code:
            issues.append({
                "title": "Use of eval()",
                "description": "eval() can execute arbitrary code and is a security risk",
                "severity": "error",
                "suggestion": "Avoid eval() and use safer alternatives like JSON.parse()"
            })
        
        # Check for innerHTML usage
        if 'innerHTML' in code:
            issues.append({
                "title": "Potential XSS Risk",
                "description": "innerHTML can lead to XSS vulnerabilities",
                "severity": "warning",
                "suggestion": "Use textContent or sanitize HTML content before insertion"
            })
        
        # Check for document.write
        if 'document.write' in code:
            issues.append({
                "title": "Use of document.write",
                "description": "document.write can cause security and performance issues",
                "severity": "warning",
                "suggestion": "Use modern DOM manipulation methods instead"
            })
        
        return issues
    
    def _check_js_performance_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for JavaScript performance issues"""
        issues = []
        
        # Check for multiple DOM queries
        dom_queries = len(re.findall(r'document\.(getElementById|querySelector|getElementsBy)', code))
        if dom_queries > 3:
            issues.append({
                "title": "Multiple DOM Queries",
                "description": f"Found {dom_queries} DOM queries which may impact performance",
                "severity": "info",
                "suggestion": "Cache DOM elements in variables to avoid repeated queries"
            })
        
        # Check for synchronous operations in loops
        if re.search(r'for\s*\([^)]*\)\s*{[^}]*(?:fetch|XMLHttpRequest)', code, re.DOTALL):
            issues.append({
                "title": "Synchronous Operations in Loop",
                "description": "Potential blocking operations inside loops",
                "severity": "warning",
                "suggestion": "Use Promise.all() or async/await for concurrent operations"
            })
        
        return issues
    
    async def _analyze_java(self, code: str) -> Dict[str, Any]:
        """Analyze Java code"""
        results = {
            "issues": [],
            "metrics": self._extract_java_metrics(code),
            "quality_indicators": {},
            "complexity_analysis": {}
        }
        
        # Basic Java analysis
        results["issues"].extend(self._check_java_issues(code))
        results["complexity_analysis"] = self._analyze_java_complexity(code)
        
        return results
    
    def _extract_java_metrics(self, code: str) -> Dict[str, Any]:
        """Extract metrics from Java code"""
        lines = code.split('\n')
        
        return {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('//')]),
            "classes": len(re.findall(r'\bclass\s+\w+', code)),
            "methods": len(re.findall(r'\b(?:public|private|protected)?\s*\w+\s+\w+\s*\([^)]*\)\s*{', code)),
            "interfaces": len(re.findall(r'\binterface\s+\w+', code)),
            "loops": len(re.findall(r'\b(for|while)\s*\(', code)),
            "conditions": len(re.findall(r'\bif\s*\(', code)),
            "try_blocks": len(re.findall(r'\btry\s*{', code)),
            "imports": len(re.findall(r'\bimport\s+', code))
        }
    
    def _check_java_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for Java-specific issues"""
        issues = []
        
        # Check for System.out.println in production code
        if 'System.out.println' in code:
            issues.append({
                "title": "Debug Print Statements",
                "description": "Found System.out.println statements",
                "severity": "info",
                "suggestion": "Use proper logging framework instead of System.out.println"
            })
        
        # Check for empty catch blocks
        if re.search(r'catch\s*\([^)]*\)\s*{\s*}', code):
            issues.append({
                "title": "Empty Catch Block",
                "description": "Empty catch blocks can hide errors",
                "severity": "warning",
                "suggestion": "Handle exceptions properly or at least log them"
            })
        
        return issues
    
    def _analyze_java_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze Java code complexity"""
        return {
            "cyclomatic_complexity": 1 + len(re.findall(r'\b(if|for|while|case|catch)\b', code)),
            "method_count": len(re.findall(r'\b(?:public|private|protected)?\s*\w+\s+\w+\s*\(', code)),
            "class_count": len(re.findall(r'\bclass\s+\w+', code))
        }
    
    async def _analyze_cpp(self, code: str) -> Dict[str, Any]:
        """Analyze C/C++ code"""
        results = {
            "issues": [],
            "metrics": self._extract_cpp_metrics(code),
            "quality_indicators": {},
            "complexity_analysis": {}
        }
        
        results["issues"].extend(self._check_cpp_issues(code))
        results["complexity_analysis"] = self._analyze_cpp_complexity(code)
        
        return results
    
    def _extract_cpp_metrics(self, code: str) -> Dict[str, Any]:
        """Extract metrics from C/C++ code"""
        lines = code.split('\n')
        
        return {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('//')]),
            "functions": len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', code)),
            "classes": len(re.findall(r'\bclass\s+\w+', code)),
            "structs": len(re.findall(r'\bstruct\s+\w+', code)),
            "includes": len(re.findall(r'#include\s*<.*>', code)),
            "loops": len(re.findall(r'\b(for|while)\s*\(', code)),
            "conditions": len(re.findall(r'\bif\s*\(', code)),
            "pointers": len(re.findall(r'\*\w+|\w+\*', code))
        }
    
    def _check_cpp_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for C/C++ specific issues"""
        issues = []
        
        # Check for potential memory leaks
        new_count = len(re.findall(r'\bnew\s+', code))
        delete_count = len(re.findall(r'\bdelete\s+', code))
        
        if new_count > delete_count:
            issues.append({
                "title": "Potential Memory Leak",
                "description": f"Found {new_count} 'new' but only {delete_count} 'delete' statements",
                "severity": "warning",
                "suggestion": "Ensure every 'new' has a corresponding 'delete' or use smart pointers"
            })
        
        # Check for unsafe functions
        unsafe_functions = ['strcpy', 'strcat', 'sprintf', 'gets']
        for func in unsafe_functions:
            if func in code:
                issues.append({
                    "title": f"Unsafe Function: {func}",
                    "description": f"Function {func} is prone to buffer overflow",
                    "severity": "warning",
                    "suggestion": f"Use safer alternatives like strncpy, strncat, snprintf, or fgets"
                })
        
        return issues
    
    def _analyze_cpp_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze C/C++ code complexity"""
        return {
            "cyclomatic_complexity": 1 + len(re.findall(r'\b(if|for|while|case|catch)\b', code)),
            "function_count": len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', code)),
            "pointer_usage": len(re.findall(r'\*\w+|\w+\*', code))
        }
    
    async def _analyze_generic(self, code: str, language: str) -> Dict[str, Any]:
        """Generic analysis for unsupported languages"""
        lines = code.split('\n')
        
        return {
            "issues": [{
                "title": f"Limited Analysis for {language}",
                "description": f"Full static analysis not available for {language}",
                "severity": "info",
                "suggestion": "Consider using language-specific tools for detailed analysis"
            }],
            "metrics": {
                "total_lines": len(lines),
                "code_lines": len([line for line in lines if line.strip()]),
                "blank_lines": len([line for line in lines if not line.strip()]),
                "estimated_functions": len(re.findall(r'\w+\s*\([^)]*\)\s*{', code)),
                "estimated_complexity": 1 + len(re.findall(r'\b(if|for|while|switch)\b', code))
            },
            "quality_indicators": {
                "has_comments": bool(re.search(r'//|/\*|\#', code)),
                "estimated_documentation_ratio": len(re.findall(r'//|/\*', code)) / max(1, len(lines))
            },
            "complexity_analysis": {
                "cyclomatic_complexity": 1 + len(re.findall(r'\b(if|for|while|case)\b', code)),
                "nesting_depth": code.count('{') // 2  # Rough estimate
            }
        }
    
    def _create_error_result(self, error_message: str, code: str, language: str) -> Dict[str, Any]:
        """Create error result when analysis fails"""
        lines = code.split('\n')
        
        return {
            "issues": [{
                "title": "Analysis Failed",
                "description": f"Static analysis failed: {error_message}",
                "severity": "error",
                "suggestion": "Check code syntax and structure"
            }],
            "metrics": {
                "total_lines": len(lines),
                "analysis_status": "failed"
            },
            "quality_indicators": {},
            "complexity_analysis": {
                "cyclomatic_complexity": 0,
                "analysis_status": "failed"
            }
        }
    
    def _check_js_syntax_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for JavaScript syntax issues"""
        issues = []
        
        # Check for missing semicolons (basic check)
        lines = code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped and not stripped.endswith((';', '{', '}', ')', ',')) and 
                not stripped.startswith(('if', 'for', 'while', 'function', 'class', '//', '/*', 'import', 'export'))):
                issues.append({
                    "title": "Missing Semicolon",
                    "description": f"Line {i+1} might be missing a semicolon",
                    "severity": "info",
                    "suggestion": "Add semicolon at the end of the statement",
                    "line_number": i+1
                })
        
        return issues
    
    def _check_js_style_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for JavaScript style issues"""
        issues = []
        
        # Check for var usage
        if 'var ' in code:
            issues.append({
                "title": "Use of 'var' keyword",
                "description": "Found usage of 'var' which has function scope",
                "severity": "warning",
                "suggestion": "Use 'let' or 'const' instead of 'var' for block scope"
            })
        
        # Check for == usage
        if re.search(r'[^=!]==[^=]', code):
            issues.append({
                "title": "Loose equality comparison",
                "description": "Found usage of '==' which can cause type coercion issues",
                "severity": "warning",
                "suggestion": "Use '===' for strict equality comparison"
            })
        
        # Check for console.log
        if 'console.log' in code:
            issues.append({
                "title": "Console statements found",
                "description": "Console.log statements should be removed in production",
                "severity": "info",
                "suggestion": "Remove console.log statements or use a proper logging library"
            })
        
        return issues
    
    def _check_js_security_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for JavaScript security issues"""
        issues = []
        
        # Check for eval usage
        if 'eval(' in code:
            issues.append({
                "title": "Use of eval()",
                "description": "eval() can execute arbitrary code and is a security risk",
                "severity": "error",
                "suggestion": "Avoid eval() and use safer alternatives like JSON.parse()"
            })
        
        # Check for innerHTML usage
        if 'innerHTML' in code:
            issues.append({
                "title": "Potential XSS vulnerability",
                "description": "Using innerHTML can lead to XSS attacks",
                "severity": "warning",
                "suggestion": "Use textContent or sanitize HTML content"
            })
        
        return issues
    
    def _check_js_performance_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for JavaScript performance issues"""
        issues = []
        
        # Check for multiple DOM queries
        dom_queries = re.findall(r'document\.(getElementById|querySelector|getElementsBy\w+)', code)
        if len(dom_queries) > 3:
            issues.append({
                "title": "Multiple DOM queries",
                "description": f"Found {len(dom_queries)} DOM queries which may impact performance",
                "severity": "info",
                "suggestion": "Cache DOM elements in variables to avoid repeated queries"
            })
        
        # Check for synchronous operations in loops
        if re.search(r'for\s*\([^)]*\)\s*{[^}]*\.(ajax|fetch)\s*\(', code, re.DOTALL):
            issues.append({
                "title": "Synchronous operations in loop",
                "description": "Performing async operations in loops can cause performance issues",
                "severity": "warning",
                "suggestion": "Use Promise.all() or async/await with proper batching"
            })
        
        return issues
    
    async def _analyze_java(self, code: str) -> Dict[str, Any]:
        """Analyze Java code"""
        results = {
            "issues": [],
            "metrics": self._extract_java_metrics(code),
            "quality_indicators": {},
            "complexity_analysis": {}
        }
        
        # Basic Java analysis
        issues = self._check_java_patterns(code)
        results["issues"].extend(issues)
        
        return results
    
    def _extract_java_metrics(self, code: str) -> Dict[str, Any]:
        """Extract metrics from Java code"""
        lines = code.split('\n')
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('//')]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "classes": len(re.findall(r'\bclass\s+\w+', code)),
            "methods": len(re.findall(r'\b(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\([^)]*\)\s*{', code)),
            "interfaces": len(re.findall(r'\binterface\s+\w+', code)),
            "loops": len(re.findall(r'\b(for|while)\s*\(', code)),
            "conditions": len(re.findall(r'\bif\s*\(', code)),
            "try_blocks": len(re.findall(r'\btry\s*{', code)),
            "imports": len(re.findall(r'\bimport\s+', code))
        }
        
        return metrics
    
    def _check_java_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Check for Java-specific issues"""
        issues = []
        
        # Check for System.out.println
        if 'System.out.println' in code:
            issues.append({
                "title": "Debug print statements",
                "description": "Found System.out.println statements",
                "severity": "info",
                "suggestion": "Use proper logging framework instead of System.out.println"
            })
        
        # Check for empty catch blocks
        if re.search(r'catch\s*\([^)]*\)\s*{\s*}', code):
            issues.append({
                "title": "Empty catch block",
                "description": "Empty catch blocks can hide exceptions",
                "severity": "warning",
                "suggestion": "Handle exceptions properly or at least log them"
            })
        
        return issues
    
    async def _analyze_cpp(self, code: str) -> Dict[str, Any]:
        """Analyze C/C++ code"""
        results = {
            "issues": [],
            "metrics": self._extract_cpp_metrics(code),
            "quality_indicators": {},
            "complexity_analysis": {}
        }
        
        # Basic C++ analysis
        issues = self._check_cpp_patterns(code)
        results["issues"].extend(issues)
        
        return results
    
    def _extract_cpp_metrics(self, code: str) -> Dict[str, Any]:
        """Extract metrics from C/C++ code"""
        lines = code.split('\n')
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('//')]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "functions": len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', code)),
            "classes": len(re.findall(r'\bclass\s+\w+', code)),
            "structs": len(re.findall(r'\bstruct\s+\w+', code)),
            "loops": len(re.findall(r'\b(for|while)\s*\(', code)),
            "conditions": len(re.findall(r'\bif\s*\(', code)),
            "includes": len(re.findall(r'#include\s*[<"]', code)),
            "pointers": len(re.findall(r'\*\w+|\w+\s*\*', code))
        }
        
        return metrics
    
    def _check_cpp_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Check for C/C++ specific issues"""
        issues = []
        
        # Check for memory leaks potential
        if 'new ' in code and 'delete' not in code:
            issues.append({
                "title": "Potential memory leak",
                "description": "Found 'new' without corresponding 'delete'",
                "severity": "warning",
                "suggestion": "Ensure every 'new' has a corresponding 'delete' or use smart pointers"
            })
        
        # Check for buffer overflow potential
        if re.search(r'\bgets\s*\(|\bstrcpy\s*\(|\bsprintf\s*\(', code):
            issues.append({
                "title": "Unsafe function usage",
                "description": "Using functions prone to buffer overflow",
                "severity": "error",
                "suggestion": "Use safer alternatives like fgets(), strncpy(), snprintf()"
            })
        
        return issues
    
    def _create_error_result(self, error_msg: str, code: str, language: str) -> Dict[str, Any]:
        """Create error result when analysis fails"""
        lines = code.split('\n')
        
        return {
            "issues": [{
                "title": "Analysis Error",
                "description": f"Failed to analyze {language} code: {error_msg}",
                "severity": "error",
                "suggestion": "Check code syntax and structure"
            }],
            "metrics": {
                "total_lines": len(lines),
                "code_lines": len([line for line in lines if line.strip()]),
                "functions": 0,
                "classes": 0,
                "complexity": 1
            },
            "quality_indicators": {},
            "complexity_analysis": {}
        }