#!/usr/bin/env python3
"""
Comprehensive Brand Deconstruction Testing Script
Tests the PENTAGRAM analysis functionality with various website types
"""

import asyncio
import json
import time
from services.brand_deconstruction_service import BrandDeconstructionService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BrandDeconstructionTester:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment")
        
        self.service = BrandDeconstructionService(self.api_key)
        self.test_results = []
    
    async def test_website(self, url: str, brand_type: str) -> dict:
        """Test brand deconstruction for a specific website"""
        print(f"\n🔍 Testing {brand_type}: {url}")
        start_time = time.time()
        
        try:
            result = await self.service.deconstruct_brand(url)
            
            test_result = {
                'url': url,
                'brand_type': brand_type,
                'success': result.get('success', False),
                'processing_time': result.get('processing_time', time.time() - start_time),
                'brand_name': result.get('brand_name', 'Unknown'),
                'has_pentagram': bool(result.get('pentagram_analysis')),
                'has_ultra_prompt': bool(result.get('ultra_fidelity_prompt')),
                'timestamp': time.time()
            }
            
            if result.get('success'):
                pentagram = result.get('pentagram_analysis', {})
                test_result.update({
                    'pentagram_fields': {
                        'center_essence': bool(pentagram.get('center_essence')),
                        'physicality': bool(pentagram.get('physicality')),
                        'environment': bool(pentagram.get('environment')),
                        'narrative': bool(pentagram.get('narrative')),
                        'texture': bool(pentagram.get('texture')),
                        'atmosphere': bool(pentagram.get('atmosphere')),
                        'geometry': bool(pentagram.get('geometry')),
                        'rendering': bool(pentagram.get('rendering')),
                        'art_direction': bool(pentagram.get('art_direction')),
                        'motion_absence': bool(pentagram.get('motion_absence')),
                        'satirical_angle': bool(pentagram.get('satirical_angle')),
                        'vulnerability_theme': bool(pentagram.get('vulnerability_theme'))
                    },
                    'sample_essence': pentagram.get('center_essence', '')[:100] + '...' if pentagram.get('center_essence') else '',
                    'ultra_prompt_length': len(result.get('ultra_fidelity_prompt', ''))
                })
                
                print(f"✅ Success - {test_result['brand_name']}")
                print(f"   📊 Processing time: {test_result['processing_time']:.2f}s")
                print(f"   🎭 Essence: {test_result['sample_essence']}")
            else:
                test_result['error'] = result.get('error', 'Unknown error')
                print(f"❌ Failed - {test_result['error']}")
                
        except Exception as e:
            test_result = {
                'url': url,
                'brand_type': brand_type,
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time,
                'timestamp': time.time()
            }
            print(f"❌ Exception - {str(e)}")
        
        self.test_results.append(test_result)
        return test_result
    
    async def run_comprehensive_test(self):
        """Run tests on various types of websites"""
        print("🚀 Starting Brand Deconstruction Comprehensive Test")
        print("=" * 60)
        
        test_websites = [
            ("https://www.apple.com", "Tech Giant"),
            ("https://www.nike.com", "Apparel/Sports"),
            ("https://www.starbucks.com", "Food & Beverage"),
            ("https://www.tesla.com", "Automotive/Innovation"),
            ("https://www.airbnb.com", "Platform/Service"),
            ("https://www.mcdonalds.com", "Fast Food"),
            ("https://www.google.com", "Search/Tech")
        ]
        
        # Run tests sequentially to avoid rate limiting
        for url, brand_type in test_websites:
            await self.test_website(url, brand_type)
            # Small delay between requests
            await asyncio.sleep(2)
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 BRAND DECONSTRUCTION TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get('success'))
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        if successful_tests > 0:
            avg_processing_time = sum(r.get('processing_time', 0) for r in self.test_results if r.get('success')) / successful_tests
            print(f"Average Processing Time: {avg_processing_time:.2f}s")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 60)
        
        for result in self.test_results:
            status = "✅" if result.get('success') else "❌"
            print(f"{status} {result['brand_type']} - {result.get('brand_name', 'Unknown')}")
            print(f"   URL: {result['url']}")
            print(f"   Time: {result.get('processing_time', 0):.2f}s")
            
            if result.get('success') and result.get('pentagram_fields'):
                completed_fields = sum(1 for v in result['pentagram_fields'].values() if v)
                total_fields = len(result['pentagram_fields'])
                print(f"   PENTAGRAM: {completed_fields}/{total_fields} fields completed")
                print(f"   Ultra Prompt: {result.get('ultra_prompt_length', 0)} characters")
            elif result.get('error'):
                print(f"   Error: {result['error']}")
            print()
        
        # Save detailed report
        report_filename = f"brand_deconstruction_test_report_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'failed_tests': failed_tests,
                    'success_rate': successful_tests/total_tests*100 if total_tests > 0 else 0,
                    'average_processing_time': avg_processing_time if successful_tests > 0 else 0
                },
                'detailed_results': self.test_results,
                'timestamp': time.time()
            }, f, indent=2)
        
        print(f"📄 Detailed report saved: {report_filename}")

async def main():
    """Main test runner"""
    try:
        tester = BrandDeconstructionTester()
        await tester.run_comprehensive_test()
    except Exception as e:
        print(f"❌ Test runner failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
