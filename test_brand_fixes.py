#!/usr/bin/env python3
"""
Brand Deconstruction Fixes Validation Test
Tests that all the critical fixes are working properly
"""

import sys
import os
import asyncio
import time

def test_imports():
    """Test that all critical imports work"""
    print("🔍 Testing imports...")
    
    try:
        # Test brand agents import
        sys.path.append('/Users/cpconnor/projects/UnifiedAIPlatform/VectorDBRAG')
        from agents.enhanced.brand_agents import (
            BrandDeconstructionAgent, 
            BrandIntelligenceAgent, 
            GPTImageGenerationAgent,
            BrandAnalysisRequest,
            BrandAnalysisResult
        )
        print("✅ Brand agents import successful")
        
        # Test service import
        from services.brand_deconstruction_service import BrandDeconstructionService
        print("✅ Brand deconstruction service import successful")
        
        # Test shared framework import
        from shared_agents.core.agent_factory import AgentBase, AgentResponse, AgentCapability
        from shared_agents.core.brand_capabilities import BrandCapability
        print("✅ Shared framework imports successful")
        
        # Store classes globally for other tests
        globals()['BrandDeconstructionAgent'] = BrandDeconstructionAgent
        globals()['BrandIntelligenceAgent'] = BrandIntelligenceAgent
        globals()['GPTImageGenerationAgent'] = GPTImageGenerationAgent
        globals()['BrandDeconstructionService'] = BrandDeconstructionService
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_agent_functionality():
    """Test that agents can be instantiated and executed"""
    print("\n🧪 Testing agent functionality...")
    
    try:
        # Test BrandDeconstructionAgent
        brand_agent = BrandDeconstructionAgent()
        test_data = {
            'brand_name': 'Test Brand',
            'website_url': 'https://example.com'
        }
        
        response = await brand_agent.execute(test_data)
        if response.success:
            print("✅ BrandDeconstructionAgent execution successful")
        else:
            print(f"❌ BrandDeconstructionAgent execution failed: {response.error}")
            return False
        
        # Test BrandIntelligenceAgent
        intel_agent = BrandIntelligenceAgent()
        intel_data = {
            'query': 'Test market analysis',
            'intelligence_type': 'market_trends'
        }
        
        intel_response = await intel_agent.execute(intel_data)
        if intel_response.success:
            print("✅ BrandIntelligenceAgent execution successful")
        else:
            print(f"❌ BrandIntelligenceAgent execution failed: {intel_response.error}")
            return False
        
        # Test GPTImageGenerationAgent
        image_agent = GPTImageGenerationAgent()
        image_data = {
            'prompt': 'Test image prompt',
            'brand_context': {'brand_name': 'Test Brand'}
        }
        
        image_response = await image_agent.execute(image_data)
        if image_response.success:
            print("✅ GPTImageGenerationAgent execution successful")
        else:
            print(f"❌ GPTImageGenerationAgent execution failed: {image_response.error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Agent functionality test failed: {e}")
        return False

def test_service_instantiation():
    """Test that the service can be instantiated"""
    print("\n⚙️ Testing service instantiation...")
    
    try:
        # Test with dummy API key
        service = BrandDeconstructionService("test-api-key")
        print("✅ BrandDeconstructionService instantiation successful")
        return True
        
    except Exception as e:
        print(f"❌ Service instantiation failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Brand Deconstruction Fixes Validation")
    print("=" * 50)
    
    # Track test results
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Service instantiation
    if test_service_instantiation():
        tests_passed += 1
    
    # Test 3: Agent functionality
    if await test_agent_functionality():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! Brand Deconstruction fixes are working correctly.")
        return True
    else:
        print(f"\n💥 {total_tests - tests_passed} test(s) failed. Some issues remain.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
