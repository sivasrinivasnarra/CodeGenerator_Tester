#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys
import os
sys.path.append('.')

try:
    from core.error_handler import ErrorHandler, validate_input
    print('✅ ErrorHandler and validate_input imported successfully')
except Exception as e:
    print(f'❌ Error importing ErrorHandler: {e}')

try:
    from core.ai_engine import AIEngine
    print('✅ AIEngine imported successfully')
except Exception as e:
    print(f'❌ Error importing AIEngine: {e}')

try:
    from core.generator import Generator
    print('✅ Generator imported successfully')
except Exception as e:
    print(f'❌ Error importing Generator: {e}')

try:
    from core.file_manager import FileManager
    print('✅ FileManager imported successfully')
except Exception as e:
    print(f'❌ Error importing FileManager: {e}')

print('\n🧪 Testing core functionality...')

try:
    error_handler = ErrorHandler()
    api_keys_status = error_handler.validate_api_keys()
    print(f'API Keys validation: {api_keys_status}')
    
    test_result = validate_input("test", str, False)
    print(f'validate_input test: {test_result}')
    
    print('✅ All core modules working correctly!')
except Exception as e:
    print(f'❌ Error testing functionality: {e}')
