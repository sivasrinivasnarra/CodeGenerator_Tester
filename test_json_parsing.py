#!/usr/bin/env python3
"""
Test script for JSON parsing functionality
"""

import json
import re

def test_json_parsing():
    """Test JSON parsing with different response formats"""
    
    print("🧪 Testing JSON Parsing")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Clean JSON Array",
            "response": '[{"id": 1, "name": "Python Stack", "language": "Python"}]',
            "expected": "Should parse successfully"
        },
        {
            "name": "JSON with Markdown",
            "response": '```json\n[{"id": 1, "name": "Python Stack", "language": "Python"}]\n```',
            "expected": "Should remove markdown and parse"
        },
        {
            "name": "JSON with Extra Text",
            "response": 'Here are the tech stack options:\n[{"id": 1, "name": "Python Stack", "language": "Python"}]',
            "expected": "Should extract JSON array"
        },
        {
            "name": "Invalid JSON",
            "response": 'This is not valid JSON at all',
            "expected": "Should handle error gracefully"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Expected: {test_case['expected']}")
        
        try:
            # Clean the response - remove any markdown formatting
            cleaned_response = test_case['response'].strip()
            
            # Remove markdown code blocks if present
            cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            # Find JSON array
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validate the structure
                if isinstance(result, list) and len(result) > 0:
                    print("✅ Successfully parsed JSON array")
                    print(f"   Found {len(result)} items")
                    for item in result:
                        print(f"   - {item.get('name', 'Unknown')}")
                else:
                    print("❌ Invalid JSON array structure")
            else:
                # Try parsing the entire response as JSON
                result = json.loads(cleaned_response)
                if isinstance(result, list) and len(result) > 0:
                    print("✅ Successfully parsed entire response as JSON")
                else:
                    print("❌ Response is not a valid JSON array")
                    
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

def test_tech_stack_format():
    """Test the expected tech stack format"""
    
    print("\n" + "=" * 50)
    print("📋 Testing Tech Stack Format")
    print("=" * 50)
    
    # Sample tech stack data
    sample_tech_stack = [
        {
            "id": 1,
            "name": "Python Django Stack",
            "language": "Python 3.11",
            "framework": "Django 4.2",
            "database": "PostgreSQL",
            "dependencies": ["django", "psycopg2", "djangorestframework"],
            "tools": ["pip", "virtualenv", "git"],
            "deployment": "Docker + AWS",
            "pros": ["Rapid development", "Built-in admin", "Large ecosystem"],
            "cons": ["Monolithic", "Learning curve"],
            "complexity": "Intermediate",
            "estimated_time": "4-6 weeks",
            "best_use_case": "Web applications with complex business logic"
        },
        {
            "id": 2,
            "name": "React Node.js Stack",
            "language": "JavaScript/TypeScript",
            "framework": "React 18 + Node.js",
            "database": "MongoDB",
            "dependencies": ["react", "express", "mongoose"],
            "tools": ["npm", "webpack", "eslint"],
            "deployment": "Vercel + MongoDB Atlas",
            "pros": ["Fast development", "Rich ecosystem", "Scalable"],
            "cons": ["Complex setup", "Many dependencies"],
            "complexity": "Advanced",
            "estimated_time": "6-8 weeks",
            "best_use_case": "Modern web applications with real-time features"
        }
    ]
    
    print("✅ Sample tech stack format:")
    for stack in sample_tech_stack:
        print(f"\n📋 {stack['name']}")
        print(f"   Language: {stack['language']}")
        print(f"   Framework: {stack['framework']}")
        print(f"   Database: {stack['database']}")
        print(f"   Complexity: {stack['complexity']}")
        print(f"   Est. Time: {stack['estimated_time']}")
        print(f"   Dependencies: {', '.join(stack['dependencies'][:3])}...")
        print(f"   Pros: {', '.join(stack['pros'][:2])}...")
        print(f"   Cons: {', '.join(stack['cons'][:2])}...")

if __name__ == "__main__":
    test_json_parsing()
    test_tech_stack_format()
    
    print("\n" + "=" * 50)
    print("🎉 JSON Parsing Tests Completed!")
    print("=" * 50) 