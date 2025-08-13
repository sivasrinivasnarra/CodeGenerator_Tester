"""
Core module for AI-powered development assistant.

This module provides the main components for the AI-powered development assistant:
- AIEngine: Handles AI model interactions and template management
- Generator: Handles code and test generation
- ErrorHandler: Handles error management and code analysis
- FileManager: Handles file operations and Docker sandbox
"""

try:
    from .ai_engine import AIEngine
    from .generator import Generator
    from .error_handler import ErrorHandler
    from .file_manager import FileManager
    
    __all__ = [
        'AIEngine',
        'Generator', 
        'ErrorHandler',
        'FileManager'
    ]
    
    # Version information
    __version__ = '1.0.0'
    
except ImportError as e:
    print(f"Error importing core modules: {e}")
    raise 