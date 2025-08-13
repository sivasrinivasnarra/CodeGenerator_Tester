"""
Integrated Error Handler and Code Analyzer module for comprehensive error handling, validation, and code analysis.
"""

import os
import logging
import traceback
import ast
import re
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json
from pathlib import Path

class ErrorHandler:
    """Handles errors, validation, code analysis, and provides error recovery mechanisms."""
    
    def __init__(self):
        self.error_log = []
        self.validation_rules = {}
        self.recovery_strategies = {}
        self.complexity_thresholds = {
            "low": 5,
            "medium": 10,
            "high": 20
        }
        self._setup_default_validation_rules()
        self._setup_recovery_strategies()
    
    def _setup_default_validation_rules(self):
        """Setup default validation rules."""
        self.validation_rules = {
            "requirement": {
                "min_length": 10,
                "max_length": 1000,
                "required_fields": ["description"],
                "forbidden_patterns": ["<script>", "javascript:"]
            },
            "code": {
                "min_length": 5,
                "max_length": 50000,
                "required_patterns": ["def ", "class ", "import "],
                "forbidden_patterns": ["eval(", "exec(", "__import__"]
            },
            "test": {
                "min_length": 10,
                "max_length": 10000,
                "required_patterns": ["def test_", "assert "],
                "forbidden_patterns": ["print(", "input("]
            }
        }
    
    def _setup_recovery_strategies(self):
        """Setup error recovery strategies."""
        self.recovery_strategies = {
            "validation_error": self._handle_validation_error,
            "syntax_error": self._handle_syntax_error,
            "runtime_error": self._handle_runtime_error,
            "ai_model_error": self._handle_ai_model_error,
            "file_error": self._handle_file_error
        }
    
    def validate_requirement(self, requirement: str) -> Dict[str, Any]:
        """Validate requirement description."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        rules = self.validation_rules.get("requirement", {})
        
        # Check length
        if len(requirement) < rules.get("min_length", 10):
            validation_result["errors"].append(
                f"Requirement too short. Minimum {rules['min_length']} characters required."
            )
            validation_result["valid"] = False
        
        if len(requirement) > rules.get("max_length", 1000):
            validation_result["warnings"].append(
                f"Requirement very long. Consider breaking it down."
            )
        
        # Check for forbidden patterns
        for pattern in rules.get("forbidden_patterns", []):
            if pattern.lower() in requirement.lower():
                validation_result["errors"].append(
                    f"Forbidden pattern detected: {pattern}"
                )
                validation_result["valid"] = False
        
        # Check for required content
        if "function" not in requirement.lower() and "class" not in requirement.lower():
            validation_result["suggestions"].append(
                "Consider specifying if you need a function or class implementation."
            )
        
        return validation_result
    
    def validate_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Validate generated code."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        rules = self.validation_rules.get("code", {})
        
        # Check length
        if len(code) < rules.get("min_length", 5):
            validation_result["errors"].append("Generated code too short.")
            validation_result["valid"] = False
        
        if len(code) > rules.get("max_length", 50000):
            validation_result["warnings"].append("Generated code very long.")
        
        # Check for required patterns
        required_patterns = rules.get("required_patterns", [])
        for pattern in required_patterns:
            if pattern not in code:
                validation_result["warnings"].append(
                    f"Missing expected pattern: {pattern}"
                )
        
        # Check for forbidden patterns
        for pattern in rules.get("forbidden_patterns", []):
            if pattern in code:
                validation_result["errors"].append(
                    f"Security risk detected: {pattern}"
                )
                validation_result["valid"] = False
        
        # Language-specific validation
        if language.lower() == "python":
            python_validation = self._validate_python_code(code)
            validation_result["errors"].extend(python_validation["errors"])
            validation_result["warnings"].extend(python_validation["warnings"])
            validation_result["valid"] = validation_result["valid"] and python_validation["valid"]
        
        return validation_result
    
    def _validate_python_code(self, code: str) -> Dict[str, Any]:
        """Validate Python-specific code patterns."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for basic Python structure
        if "import" not in code and "from" not in code:
            validation_result["warnings"].append("No imports found in code.")
        
        if "def " not in code and "class " not in code:
            validation_result["warnings"].append("No functions or classes found in code.")
        
        # Check for proper error handling
        if "try:" in code and "except" not in code:
            validation_result["errors"].append("Incomplete try-except block.")
            validation_result["valid"] = False
        
        # Check for logging
        if "logging" not in code and "print(" in code:
            validation_result["suggestions"].append("Consider using logging instead of print statements.")
        
        return validation_result
    
    def validate_tests(self, test_code: str, language: str = "python") -> Dict[str, Any]:
        """Validate generated test code."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        rules = self.validation_rules.get("test", {})
        
        # Check length
        if len(test_code) < rules.get("min_length", 10):
            validation_result["errors"].append("Generated tests too short.")
            validation_result["valid"] = False
        
        # Check for required patterns
        required_patterns = rules.get("required_patterns", [])
        for pattern in required_patterns:
            if pattern not in test_code:
                validation_result["warnings"].append(
                    f"Missing expected test pattern: {pattern}"
                )
        
        # Check for forbidden patterns
        for pattern in rules.get("forbidden_patterns", []):
            if pattern in test_code:
                validation_result["warnings"].append(
                    f"Test contains interactive elements: {pattern}"
                )
        
        # Language-specific test validation
        if language.lower() == "python":
            python_test_validation = self._validate_python_tests(test_code)
            validation_result["errors"].extend(python_test_validation["errors"])
            validation_result["warnings"].extend(python_test_validation["warnings"])
            validation_result["valid"] = validation_result["valid"] and python_test_validation["valid"]
        
        return validation_result
    
    def _validate_python_tests(self, test_code: str) -> Dict[str, Any]:
        """Validate Python-specific test patterns."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for pytest imports
        if "pytest" not in test_code and "unittest" not in test_code:
            validation_result["warnings"].append("No testing framework imports found.")
        
        # Check for test functions
        if "def test_" not in test_code:
            validation_result["warnings"].append("No test functions found.")
        
        # Check for assertions
        if "assert " not in test_code:
            validation_result["warnings"].append("No assertions found in tests.")
        
        return validation_result
    
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle errors and attempt recovery."""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
            "recovered": False,
            "recovery_action": None
        }
        
        # Log the error
        self.error_log.append(error_info)
        logging.error(f"Error in {context}: {error}")
        
        # Attempt recovery
        error_type = type(error).__name__.lower()
        for strategy_name, strategy_func in self.recovery_strategies.items():
            if strategy_name in error_type or error_type in strategy_name:
                try:
                    recovery_result = strategy_func(error, context)
                    error_info["recovered"] = recovery_result.get("success", False)
                    error_info["recovery_action"] = recovery_result.get("action", None)
                    break
                except Exception as recovery_error:
                    logging.error(f"Recovery failed: {recovery_error}")
        
        return error_info
    
    def _handle_validation_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle validation errors."""
        return {
            "success": True,
            "action": "Provide validation feedback to user",
            "suggestion": "Please review and correct the input data."
        }
    
    def _handle_syntax_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle syntax errors."""
        return {
            "success": True,
            "action": "Attempt code reformatting",
            "suggestion": "The generated code has syntax issues that need manual review."
        }
    
    def _handle_runtime_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle runtime errors."""
        return {
            "success": False,
            "action": "Log error and continue",
            "suggestion": "Runtime error occurred. Check the generated code for issues."
        }
    
    def _handle_ai_model_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle AI model errors."""
        return {
            "success": True,
            "action": "Use fallback generation method",
            "suggestion": "AI model unavailable. Using template-based generation."
        }
    
    def _handle_file_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle file operation errors."""
        return {
            "success": True,
            "action": "Create directory and retry",
            "suggestion": "File operation failed. Check permissions and disk space."
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors."""
        if not self.error_log:
            return {"total_errors": 0, "recovery_rate": 100.0}
        
        total_errors = len(self.error_log)
        recovered_errors = sum(1 for error in self.error_log if error.get("recovered", False))
        recovery_rate = (recovered_errors / total_errors) * 100
        
        error_types = {}
        for error in self.error_log:
            error_type = error.get("error_type", "Unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": total_errors,
            "recovered_errors": recovered_errors,
            "recovery_rate": round(recovery_rate, 2),
            "error_types": error_types,
            "recent_errors": self.error_log[-5:]  # Last 5 errors
        }
    
    def clear_error_log(self):
        """Clear the error log."""
        self.error_log.clear()
    
    def export_error_log(self, file_path: str = None) -> str:
        """Export error log to file."""
        if not file_path:
            file_path = f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(file_path, 'w') as f:
            json.dump(self.error_log, f, indent=2)
        
        return file_path
    
    # Code Analysis Methods (integrated from CodeAnalyzer)
    
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Comprehensive code analysis."""
        analysis = {
            "language": language,
            "metrics": {},
            "structure": {},
            "complexity": "low",
            "quality_score": 0,
            "issues": [],
            "suggestions": []
        }
        
        try:
            if language.lower() == "python":
                analysis.update(self._analyze_python_code(code))
            else:
                analysis.update(self._analyze_generic_code(code, language))
                
        except Exception as e:
            analysis["issues"].append(f"Analysis error: {e}")
        
        return analysis
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code specifically."""
        analysis = {
            "metrics": {},
            "structure": {},
            "complexity": "low",
            "quality_score": 0
        }
        
        try:
            tree = ast.parse(code)
            
            # Basic metrics
            analysis["metrics"] = self._calculate_python_metrics(tree, code)
            
            # Code structure
            analysis["structure"] = self._analyze_python_structure(tree)
            
            # Complexity analysis
            analysis["complexity"] = self._calculate_complexity(analysis["metrics"])
            
            # Quality score
            analysis["quality_score"] = self._calculate_quality_score(analysis)
            
        except SyntaxError as e:
            analysis["issues"] = [f"Syntax error: {e}"]
        except Exception as e:
            analysis["issues"] = [f"Analysis error: {e}"]
        
        return analysis
    
    def _calculate_python_metrics(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Calculate Python-specific metrics."""
        metrics = {
            "lines_of_code": len(code.split('\n')),
            "characters": len(code),
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "variables": 0,
            "comments": 0,
            "docstrings": 0,
            "complexity_score": 0
        }
        
        # Count different elements
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["functions"] += 1
                metrics["complexity_score"] += self._calculate_function_complexity(node)
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics["imports"] += 1
            elif isinstance(node, ast.Assign):
                metrics["variables"] += 1
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                metrics["docstrings"] += 1
        
        # Count comments
        comment_lines = [line for line in code.split('\n') if line.strip().startswith('#')]
        metrics["comments"] = len(comment_lines)
        
        return metrics
    
    def _analyze_python_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze Python code structure."""
        structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "nested_levels": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                structure["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [d.id for d in node.decorator_list if hasattr(d, 'id')],
                    "line_count": len(node.body) if node.body else 0
                })
            elif isinstance(node, ast.ClassDef):
                structure["classes"].append({
                    "name": node.name,
                    "bases": [base.id for base in node.bases if hasattr(base, 'id')],
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    "line_count": len(node.body)
                })
            elif isinstance(node, ast.Import):
                structure["imports"].extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                structure["imports"].append(f"{node.module}.{', '.join([alias.name for alias in node.names])}")
        
        return structure
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_complexity(self, metrics: Dict[str, Any]) -> str:
        """Calculate overall complexity level."""
        total_complexity = metrics.get("complexity_score", 0)
        
        if total_complexity <= self.complexity_thresholds["low"]:
            return "low"
        elif total_complexity <= self.complexity_thresholds["medium"]:
            return "medium"
        else:
            return "high"
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)."""
        score = 100.0
        metrics = analysis.get("metrics", {})
        
        # Penalize high complexity
        complexity_score = metrics.get("complexity_score", 0)
        if complexity_score > 20:
            score -= 20
        elif complexity_score > 10:
            score -= 10
        
        # Penalize lack of documentation
        if metrics.get("docstrings", 0) == 0:
            score -= 15
        
        # Penalize lack of comments
        comment_ratio = metrics.get("comments", 0) / max(metrics.get("lines_of_code", 1), 1)
        if comment_ratio < 0.1:
            score -= 10
        
        # Penalize very long functions
        functions = analysis.get("structure", {}).get("functions", [])
        long_functions = sum(1 for f in functions if f.get("line_count", 0) > 20)
        if long_functions > 0:
            score -= long_functions * 5
        
        return max(0, score)
    
    def _analyze_generic_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze generic code (non-Python)."""
        analysis = {
            "metrics": {
                "lines_of_code": len(code.split('\n')),
                "characters": len(code),
                "comments": len([line for line in code.split('\n') if line.strip().startswith('//') or line.strip().startswith('/*')])
            },
            "structure": {
                "functions": [],
                "classes": [],
                "imports": []
            },
            "complexity": "low",
            "quality_score": 50.0
        }
        
        # Basic pattern matching for common languages
        if language.lower() in ["javascript", "typescript"]:
            analysis["structure"]["functions"] = re.findall(r'function\s+(\w+)', code)
            analysis["structure"]["classes"] = re.findall(r'class\s+(\w+)', code)
        elif language.lower() in ["java", "cpp", "c"]:
            analysis["structure"]["functions"] = re.findall(r'(\w+)\s+\w+\s*\([^)]*\)\s*{', code)
            analysis["structure"]["classes"] = re.findall(r'class\s+(\w+)', code)
        
        return analysis
    
    def generate_complexity_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable complexity report."""
        metrics = analysis.get("metrics", {})
        structure = analysis.get("structure", {})
        
        report = f"""
# Code Analysis Report

## Overview
- **Language**: {analysis.get('language', 'Unknown')}
- **Complexity Level**: {analysis.get('complexity', 'Unknown').upper()}
- **Quality Score**: {analysis.get('quality_score', 0):.1f}/100

## Metrics
- **Lines of Code**: {metrics.get('lines_of_code', 0)}
- **Characters**: {metrics.get('characters', 0)}
- **Functions**: {metrics.get('functions', 0)}
- **Classes**: {metrics.get('classes', 0)}
- **Imports**: {metrics.get('imports', 0)}
- **Comments**: {metrics.get('comments', 0)}
- **Docstrings**: {metrics.get('docstrings', 0)}
- **Cyclomatic Complexity**: {metrics.get('complexity_score', 0)}

## Structure Analysis
"""
        
        if structure.get("functions"):
            report += "\n### Functions\n"
            for func in structure["functions"]:
                report += f"- **{func['name']}**: {len(func['args'])} args, {func['line_count']} lines\n"
        
        if structure.get("classes"):
            report += "\n### Classes\n"
            for cls in structure["classes"]:
                report += f"- **{cls['name']}**: {len(cls['methods'])} methods, {cls['line_count']} lines\n"
        
        if structure.get("imports"):
            report += "\n### Imports\n"
            for imp in structure["imports"][:10]:  # Show first 10
                report += f"- {imp}\n"
            if len(structure["imports"]) > 10:
                report += f"- ... and {len(structure['imports']) - 10} more\n"
        
        return report
    
    def suggest_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest code improvements based on analysis."""
        suggestions = []
        metrics = analysis.get("metrics", {})
        structure = analysis.get("structure", {})
        
        # Complexity suggestions
        if metrics.get("complexity_score", 0) > 15:
            suggestions.append("Consider breaking down complex functions into smaller, more manageable pieces")
        
        # Documentation suggestions
        if metrics.get("docstrings", 0) == 0:
            suggestions.append("Add docstrings to functions and classes for better documentation")
        
        # Comment suggestions
        comment_ratio = metrics.get("comments", 0) / max(metrics.get("lines_of_code", 1), 1)
        if comment_ratio < 0.1:
            suggestions.append("Add more inline comments to explain complex logic")
        
        # Function length suggestions
        functions = structure.get("functions", [])
        long_functions = [f for f in functions if f.get("line_count", 0) > 20]
        if long_functions:
            suggestions.append(f"Consider refactoring {len(long_functions)} long functions (over 20 lines)")
        
        # Import suggestions
        if metrics.get("imports", 0) > 20:
            suggestions.append("Consider organizing imports and removing unused ones")
        
        return suggestions 