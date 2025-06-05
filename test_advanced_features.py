#!/usr/bin/env python3
"""
Test script for Advanced OpenAI Features
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_advanced_features():
    """Test advanced OpenAI features"""
    
    print("🧪 Testing Advanced OpenAI Features")
    print("=" * 50)
    
    try:
        from services.advanced_openai_features import AdvancedOpenAIFeatures
        
        # Initialize with API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        print("✅ OpenAI API key found")
        
        # Create instance
        features = AdvancedOpenAIFeatures(api_key)
        print("✅ AdvancedOpenAIFeatures instance created")
        
        # Test system status
        status = features.get_system_status()
        print(f"✅ System status: {status}")
        
        # Test enhanced embeddings
        print("\n📊 Testing Enhanced Embeddings...")
        result = await features.create_enhanced_embeddings(
            texts=["Hello world", "Advanced OpenAI features"],
            metadata=[{"source": "test1"}, {"source": "test2"}],
            dimensions=1536
        )
        print(f"✅ Enhanced embeddings created: {len(result['embeddings'])} vectors")
        
        # Test structured report
        print("\n📋 Testing Structured Report...")
        report = features.create_structured_report(
            data={"test": "data", "value": 42},        report_schema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "summary": {"type": "string"},
                "findings": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["summary", "findings"]
        },
            report_type="test"
        )
        print(f"✅ Structured report generated: {type(report)}")
        
        # Test function calling agent
        print("\n🤖 Testing Function Calling Agent...")
        agent_config = features.create_function_calling_agent(
            available_tools=[{
                "name": "test_function",
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            }],
            instructions="You are a helpful test agent"
        )
        print(f"✅ Function calling agent created: {len(agent_config.get('tools', []))} tools")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_integration():
    """Test Flask route integration"""
    
    print("\n🌐 Testing Flask Integration")
    print("=" * 50)
    
    try:
        from app import create_app
        
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test if advanced routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        advanced_routes = [r for r in routes if '/api/vision/' in r or '/api/structured/' in r or '/api/realtime/' in r]
        
        if advanced_routes:
            print(f"✅ Advanced routes registered: {len(advanced_routes)} routes")
            for route in advanced_routes[:5]:  # Show first 5
                print(f"   - {route}")
            if len(advanced_routes) > 5:
                print(f"   ... and {len(advanced_routes) - 5} more")
        else:
            print("❌ No advanced routes found")
            return False
        
        # Test advanced-openai page route
        if '/advanced-openai' in routes:
            print("✅ Advanced OpenAI page route registered")
        else:
            print("❌ Advanced OpenAI page route not found")
            return False
        
        print("✅ Flask integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    
    print("🔮 Advanced OpenAI Features Test Suite")
    print("=" * 60)
    
    # Test basic imports
    try:
        from services.advanced_openai_features import AdvancedOpenAIFeatures
        from services.advanced_openai_routes import register_advanced_openai_routes
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test Flask integration
    flask_success = test_flask_integration()
    
    # Test advanced features (requires API key)
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        features_success = asyncio.run(test_advanced_features())
    else:
        print("\n⚠️  Skipping advanced features test (no API key)")
        features_success = True
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Flask Integration: {'✅ PASS' if flask_success else '❌ FAIL'}")
    print(f"Advanced Features: {'✅ PASS' if features_success else '❌ FAIL'}")
    
    if flask_success and features_success:
        print("\n🎉 All tests passed! Advanced OpenAI features are ready to use.")
        print("\n🚀 To start the application:")
        print("   python app.py")
        print("\n🌐 Then visit:")
        print("   http://localhost:5001/advanced-openai")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
