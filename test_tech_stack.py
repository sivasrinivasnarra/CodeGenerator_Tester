#!/usr/bin/env python3
"""
Test script for tech stack suggestion functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import AIEngine

def test_tech_stack_suggestion():
    """Test the tech stack suggestion functionality"""
    
    print("🧪 Testing Tech Stack Suggestion")
    print("=" * 50)
    
    # Initialize AI engine
    ai_engine = AIEngine()
    
    # Test requirement
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
    
    print("📋 Test Requirement:")
    print(requirement)
    
    # Test tech stack suggestion
    print("\n🔍 Testing tech stack suggestion...")
    
    prompt = f"""
    Analyze the following requirement and suggest 3-4 different technology stack options:
    
    Requirement: {requirement}
    
    For each tech stack option, provide:
    1. Programming Language (with version)
    2. Framework(s)
    3. Database (if needed)
    4. Additional libraries/dependencies
    5. Development tools
    6. Deployment considerations
    7. Pros and cons
    8. Complexity level (Beginner/Intermediate/Advanced)
    9. Estimated development time
    10. Best use case
    
    Return ONLY a valid JSON array with each tech stack option as an object:
    [
        {{
            "id": 1,
            "name": "Tech Stack Name",
            "language": "Programming Language",
            "framework": "Main Framework",
            "database": "Database Type",
            "dependencies": ["list", "of", "dependencies"],
            "tools": ["development", "tools"],
            "deployment": "Deployment method",
            "pros": ["pro1", "pro2", "pro3"],
            "cons": ["con1", "con2"],
            "complexity": "Beginner/Intermediate/Advanced",
            "estimated_time": "time estimate",
            "best_use_case": "When to use this stack"
        }}
    ]
    
    Ensure the response is valid JSON without any additional text or formatting.
    """
    
    try:
        response = ai_engine.generate_response(prompt, model="gpt-4o-mini")
        print("✅ AI Response received")
        
        # Try to parse JSON
        import json
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = response[start_idx:end_idx]
            tech_stacks = json.loads(json_str)
            print(f"✅ Successfully parsed {len(tech_stacks)} tech stack options")
            
            # Display tech stacks
            for i, stack in enumerate(tech_stacks, 1):
                print(f"\n📋 Tech Stack {i}: {stack.get('name', 'N/A')}")
                print(f"   Language: {stack.get('language', 'N/A')}")
                print(f"   Framework: {stack.get('framework', 'N/A')}")
                print(f"   Database: {stack.get('database', 'N/A')}")
                print(f"   Complexity: {stack.get('complexity', 'N/A')}")
                print(f"   Est. Time: {stack.get('estimated_time', 'N/A')}")
                
        else:
            print("❌ Could not find JSON array in response")
            print("Raw response:")
            print(response[:500] + "..." if len(response) > 500 else response)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Raw response:")
        print(response[:500] + "..." if len(response) > 500 else response)

if __name__ == "__main__":
    test_tech_stack_suggestion() 