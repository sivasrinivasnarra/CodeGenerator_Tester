"""
Code Analyzer utility for analyzing code structure and complexity.
"""

import ast
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

class CodeAnalyzer:
    """Analyzes code structure, complexity, and quality metrics."""
    
    def __init__(self):
        self.complexity_thresholds = {
            "low": 5,
            "medium": 10,
            "high": 20
        }
    
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