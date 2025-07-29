#!/usr/bin/env python3
"""
Enhanced Demo for AI-Powered Development Assistant
Showcases new features: document upload, tech stack suggestions, and improved functionality.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import AIEngine, CodeGenerator, TestGenerator, ErrorHandler
from utils.file_manager import FileManager
from utils.code_analyzer import CodeAnalyzer
from utils.templates import TemplateManager

def demo_enhanced_features():
    """Demonstrate the enhanced features of the AI-Powered Development Assistant."""
    
    print("🚀 Enhanced AI-Powered Development Assistant Demo")
    print("=" * 60)
    
    # Initialize components
    print("\n📦 Initializing components...")
    ai_engine = AIEngine()
    code_generator = CodeGenerator()
    test_generator = TestGenerator()
    error_handler = ErrorHandler()

    file_manager = FileManager()
    code_analyzer = CodeAnalyzer()
    template_manager = TemplateManager()
    
    print("✅ All components initialized successfully!")
    
    # Demo 1: Tech Stack Suggestion
    print("\n" + "=" * 60)
    print("🎯 DEMO 1: Tech Stack Suggestion")
    print("=" * 60)
    
    requirement = """
    Create a web application for managing a library system with the following features:
    - User authentication and authorization
    - Book catalog management (add, edit, delete, search)
    - Borrowing and returning books
    - Fine calculation for overdue books
    - Admin dashboard with analytics
    - RESTful API for mobile app integration
    - Real-time notifications
    - Report generation (PDF/Excel)
    """
    
    print("📋 Requirement:")
    print(requirement)
    
    print("\n🔍 Analyzing requirements and suggesting tech stack...")
    tech_stack_prompt = f"""
    Analyze the following requirement and suggest the most appropriate technology stack:
    
    Requirement: {requirement}
    
    Please provide a detailed tech stack recommendation including:
    1. Programming Language (with version)
    2. Framework(s)
    3. Database (if needed)
    4. Additional libraries/dependencies
    5. Development tools
    6. Deployment considerations
    
    Format your response as a structured recommendation with clear reasoning for each choice.
    """
    
    try:
        tech_stack = ai_engine.generate_response(tech_stack_prompt, model="gpt-4o-mini")
        print("\n🎯 Recommended Tech Stack:")
        print("-" * 40)
        print(tech_stack)
    except Exception as e:
        print(f"❌ Error suggesting tech stack: {e}")
    
    # Demo 2: Document + Prompt Processing
    print("\n" + "=" * 60)
    print("📄 DEMO 2: Document + Prompt Processing")
    print("=" * 60)
    
    # Simulate uploaded document content
    document_content = """
    TECHNICAL SPECIFICATION DOCUMENT
    
    Project: E-commerce Inventory Management System
    
    Functional Requirements:
    1. Product Management
       - Add new products with categories, SKU, pricing
       - Update product information and stock levels
       - Bulk import/export functionality
       - Image upload and management
    
    2. Inventory Tracking
       - Real-time stock level monitoring
       - Low stock alerts and notifications
       - Stock movement history and audit trail
       - Multi-warehouse support
    
    3. Order Processing
       - Order creation and management
       - Payment processing integration
       - Shipping and delivery tracking
       - Return and refund handling
    
    Technical Requirements:
    - Scalable architecture supporting 10,000+ products
    - Real-time data synchronization
    - Mobile-responsive web interface
    - API for third-party integrations
    - Comprehensive reporting and analytics
    """
    
    # Combine document with specific prompt
    specific_prompt = "Focus on the inventory tracking module with real-time stock monitoring and low stock alerts."
    
    combined_requirement = f"""
    Additional Context from Document:
    {document_content}
    
    Specific Requirements:
    {specific_prompt}
    """
    
    print("📄 Document Content (simulated):")
    print(document_content[:200] + "...")
    
    print(f"\n💭 Specific Prompt: {specific_prompt}")
    
    print("\n🔄 Combined Requirement:")
    print("-" * 40)
    print(combined_requirement[:300] + "...")
    
    # Demo 3: Enhanced Code Generation
    print("\n" + "=" * 60)
    print("🚀 DEMO 3: Enhanced Code Generation")
    print("=" * 60)
    
    simple_requirement = "Create a Python class for inventory tracking with methods to add items, remove items, check stock levels, and get low stock alerts."
    
    print("📋 Requirement:")
    print(simple_requirement)
    
    print("\n🚀 Generating code...")
    try:
        code_result = code_generator.generate_code(
            simple_requirement,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=2000
        )
        
        if code_result['success']:
            print("✅ Code generated successfully!")
            print("\n📝 Generated Code:")
            print("-" * 40)
            print(code_result['code'])
            
            # Save the code
            file_path = file_manager.save_code_file(simple_requirement, code_result['code'])
            print(f"\n💾 Code saved to: {file_path}")
            
        else:
            print(f"❌ Code generation failed: {code_result['error']}")
            
    except Exception as e:
        print(f"❌ Error during code generation: {e}")
    
    # Demo 4: Enhanced Test Generation
    print("\n" + "=" * 60)
    print("🧪 DEMO 4: Enhanced Test Generation")
    print("=" * 60)
    
    if 'code_result' in locals() and code_result['success']:
        print("🧪 Generating comprehensive test suite...")
        try:
            test_result = test_generator.generate_tests(
                simple_requirement,
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=2000
            )
            
            if test_result['success']:
                print("✅ Tests generated successfully!")
                print("\n🧪 Generated Test Suite:")
                print("-" * 40)
                print(test_result['tests'])
                
                # Save the tests
                test_file_path = file_manager.save_test_file(simple_requirement, test_result['tests'])
                print(f"\n💾 Tests saved to: {test_file_path}")
                
            else:
                print(f"❌ Test generation failed: {test_result['error']}")
                
        except Exception as e:
            print(f"❌ Error during test generation: {e}")
    else:
        print("⚠️ Skipping test generation - no code available")
    
    # Demo 5: Code Quality Assessment
    print("\n" + "=" * 60)
    print("📊 DEMO 5: Code Quality Assessment")
    print("=" * 60)
    
    print("📊 Analyzing code quality...")
    try:
        if 'code_result' in locals() and code_result['success']:
            analysis = code_analyzer.analyze_code(code_result['code'])
            
            print("✅ Code quality assessment completed!")
            
            score = analysis.get('quality_score', 0)
            print(f"\n📊 Code Quality Score: {score:.1f}/100")
            
            if score >= 80:
                print("🎉 Excellent! Your code is high quality")
            elif score >= 60:
                print("⚠️ Good, but some improvements recommended")
            else:
                print("❌ Significant improvements needed")
            
            print("\n📋 Analysis Results:")
            print("-" * 40)
            print(f"  Complexity: {analysis.get('complexity', 'N/A')}")
            print(f"  Lines of Code: {analysis.get('loc', 0)}")
            print(f"  Functions: {analysis.get('function_count', 0)}")
            print(f"  Classes: {analysis.get('class_count', 0)}")
            
        else:
            print("⚠️ Skipping code quality assessment - no code available")
            
    except Exception as e:
        print(f"❌ Error during assessment: {e}")
    
    # Demo 6: File Management
    print("\n" + "=" * 60)
    print("📁 DEMO 6: Enhanced File Management")
    print("=" * 60)
    
    files = file_manager.list_generated_files()
    
    print("📄 Generated Files:")
    for file_type, file_list in files.items():
        if file_list:
            print(f"\n{file_type.upper()} Files:")
            for file_path in file_list:
                file_info = file_manager.get_file_info(file_path)
                print(f"  📄 {file_info['name']} ({file_info['size']} bytes)")
    
    # Demo 7: Code Analysis
    print("\n" + "=" * 60)
    print("📊 DEMO 7: Code Analysis")
    print("=" * 60)
    
    if 'code_result' in locals() and code_result['success']:
        print("📊 Analyzing code quality...")
        try:
            analysis = code_analyzer.analyze_code(code_result['code'])
            
            print("✅ Code analysis completed!")
            print(f"\n📊 Analysis Results:")
            print(f"  Complexity Score: {analysis['complexity_score']:.2f}")
            print(f"  Lines of Code: {analysis['loc']}")
            print(f"  Functions: {analysis['function_count']}")
            print(f"  Classes: {analysis['class_count']}")
            print(f"  Imports: {analysis['import_count']}")
            print(f"  Comments: {analysis['comment_count']}")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
    else:
        print("⚠️ Skipping code analysis - no code available")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced Demo Completed!")
    print("=" * 60)
    
    print("\n✨ New Features Demonstrated:")
    print("  ✅ Tech Stack Suggestions")
    print("  ✅ Document + Prompt Processing")
    print("  ✅ Enhanced Code Generation")
    print("  ✅ Comprehensive Test Generation")
    print("  ✅ Code Quality Assessment")
    print("  ✅ Advanced File Management")
    print("  ✅ Code Quality Analysis")
    
    print("\n🚀 Ready to use the enhanced AI-Powered Development Assistant!")
    print("   Run: streamlit run app.py")

if __name__ == "__main__":
    demo_enhanced_features() 