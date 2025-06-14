#!/usr/bin/env python3
"""
Performance comparison script between original and optimized API versions
Demonstrates the improvements from async HTTP client and concurrent model calls
"""

import asyncio
import time
import statistics
import json
from typing import List, Dict, Any
import httpx
import requests
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"
OPTIMIZED_API_BASE_URL = "http://localhost:8001"  # Assuming optimized runs on different port
API_KEY = "87ea1604be1f6_02f173F5fb67582e647fcef6c40"

TEST_QUESTIONS = [
    "What are the best practices for sustainable urban development?",
    "How can AI improve healthcare outcomes?",
    "What are the key challenges in renewable energy adoption?",
    "How can we address climate change through technology?",
    "What are the ethical implications of artificial intelligence?",
    "How can blockchain technology transform finance?",
    "What are the benefits of remote work for organizations?",
    "How can we improve cybersecurity in the digital age?",
    "What role does data science play in business decision making?",
    "How can we promote digital literacy in education?"
]

class PerformanceTester:
    def __init__(self, base_url: str, api_key: str, name: str):
        self.base_url = base_url
        self.api_key = api_key
        self.name = name
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def test_async_concurrent(self, questions: List[str], max_concurrent: int = 5) -> Dict[str, Any]:
        """Test async concurrent requests"""
        print(f"\n🚀 Testing {self.name} - Async Concurrent ({max_concurrent} concurrent)")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def make_request(question: str) -> Dict[str, Any]:
                async with semaphore:
                    start_time = time.time()
                    try:
                        response = await client.post(
                            f"{self.base_url}/consensus",
                            headers=self.headers,
                            json={
                                "question": question,
                                "max_models": 3,
                                "enable_caching": False  # Disable caching for fair comparison
                            }
                        )
                        end_time = time.time()
                        
                        if response.status_code == 200:
                            data = response.json()
                            return {
                                "success": True,
                                "response_time": end_time - start_time,
                                "consensus_score": data.get("consensus_score", 0),
                                "models_used": len(data.get("models_used", [])),
                                "question": question
                            }
                        else:
                            return {
                                "success": False,
                                "response_time": end_time - start_time,
                                "error": f"HTTP {response.status_code}",
                                "question": question
                            }
                    except Exception as e:
                        return {
                            "success": False,
                            "response_time": time.time() - start_time,
                            "error": str(e),
                            "question": question
                        }
            
            start_total = time.time()
            results = await asyncio.gather(*[make_request(q) for q in questions])
            end_total = time.time()
            
            return self._analyze_results(results, end_total - start_total)
    
    def test_sync_sequential(self, questions: List[str]) -> Dict[str, Any]:
        """Test synchronous sequential requests"""
        print(f"\n🐌 Testing {self.name} - Sync Sequential")
        
        results = []
        start_total = time.time()
        
        for question in questions:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/consensus",
                    headers=self.headers,
                    json={
                        "question": question,
                        "max_models": 3,
                        "enable_caching": False
                    },
                    timeout=60
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "success": True,
                        "response_time": end_time - start_time,
                        "consensus_score": data.get("consensus_score", 0),
                        "models_used": len(data.get("models_used", [])),
                        "question": question
                    })
                else:
                    results.append({
                        "success": False,
                        "response_time": end_time - start_time,
                        "error": f"HTTP {response.status_code}",
                        "question": question
                    })
            except Exception as e:
                results.append({
                    "success": False,
                    "response_time": time.time() - start_time,
                    "error": str(e),
                    "question": question
                })
        
        end_total = time.time()
        return self._analyze_results(results, end_total - start_total)
    
    def test_sync_concurrent(self, questions: List[str], max_workers: int = 5) -> Dict[str, Any]:
        """Test synchronous concurrent requests using ThreadPoolExecutor"""
        print(f"\n⚡ Testing {self.name} - Sync Concurrent ({max_workers} threads)")
        
        def make_request(question: str) -> Dict[str, Any]:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/consensus",
                    headers=self.headers,
                    json={
                        "question": question,
                        "max_models": 3,
                        "enable_caching": False
                    },
                    timeout=60
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "response_time": end_time - start_time,
                        "consensus_score": data.get("consensus_score", 0),
                        "models_used": len(data.get("models_used", [])),
                        "question": question
                    }
                else:
                    return {
                        "success": False,
                        "response_time": end_time - start_time,
                        "error": f"HTTP {response.status_code}",
                        "question": question
                    }
            except Exception as e:
                return {
                    "success": False,
                    "response_time": time.time() - start_time,
                    "error": str(e),
                    "question": question
                }
        
        start_total = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(make_request, questions))
        end_total = time.time()
        
        return self._analyze_results(results, end_total - start_total)
    
    def _analyze_results(self, results: List[Dict[str, Any]], total_time: float) -> Dict[str, Any]:
        """Analyze test results"""
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        if successful:
            response_times = [r["response_time"] for r in successful]
            consensus_scores = [r["consensus_score"] for r in successful]
            
            analysis = {
                "total_requests": len(results),
                "successful_requests": len(successful),
                "failed_requests": len(failed),
                "success_rate": len(successful) / len(results) * 100,
                "total_time": total_time,
                "avg_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "std_response_time": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "avg_consensus_score": statistics.mean(consensus_scores),
                "requests_per_second": len(successful) / total_time,
                "errors": [r["error"] for r in failed] if failed else []
            }
        else:
            analysis = {
                "total_requests": len(results),
                "successful_requests": 0,
                "failed_requests": len(failed),
                "success_rate": 0,
                "total_time": total_time,
                "errors": [r["error"] for r in failed]
            }
        
        return analysis


def print_results(results: Dict[str, Any], test_name: str):
    """Pretty print test results"""
    print(f"\n📊 Results for {test_name}:")
    print("=" * 50)
    print(f"Total Requests: {results['total_requests']}")
    print(f"Successful: {results['successful_requests']}")
    print(f"Failed: {results['failed_requests']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Total Time: {results['total_time']:.2f}s")
    
    if results['successful_requests'] > 0:
        print(f"Average Response Time: {results['avg_response_time']:.2f}s")
        print(f"Median Response Time: {results['median_response_time']:.2f}s")
        print(f"Min Response Time: {results['min_response_time']:.2f}s")
        print(f"Max Response Time: {results['max_response_time']:.2f}s")
        print(f"Std Dev Response Time: {results['std_response_time']:.2f}s")
        print(f"Average Consensus Score: {results['avg_consensus_score']:.3f}")
        print(f"Requests per Second: {results['requests_per_second']:.2f}")
    
    if results.get('errors'):
        print(f"Errors: {results['errors'][:3]}...")  # Show first 3 errors


def create_comparison_chart(original_results: Dict[str, Dict], optimized_results: Dict[str, Dict]):
    """Create performance comparison charts"""
    print("\n📈 Creating performance comparison charts...")
    
    # Prepare data for plotting
    test_types = list(original_results.keys())
    
    # Response time comparison
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Average response time comparison
    orig_times = [original_results[t].get('avg_response_time', 0) for t in test_types]
    opt_times = [optimized_results[t].get('avg_response_time', 0) for t in test_types]
    
    x = range(len(test_types))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], orig_times, width, label='Original', alpha=0.8, color='red')
    ax1.bar([i + width/2 for i in x], opt_times, width, label='Optimized', alpha=0.8, color='green')
    ax1.set_xlabel('Test Type')
    ax1.set_ylabel('Average Response Time (s)')
    ax1.set_title('Average Response Time Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(test_types, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Total time comparison
    orig_total = [original_results[t].get('total_time', 0) for t in test_types]
    opt_total = [optimized_results[t].get('total_time', 0) for t in test_types]
    
    ax2.bar([i - width/2 for i in x], orig_total, width, label='Original', alpha=0.8, color='red')
    ax2.bar([i + width/2 for i in x], opt_total, width, label='Optimized', alpha=0.8, color='green')
    ax2.set_xlabel('Test Type')
    ax2.set_ylabel('Total Time (s)')
    ax2.set_title('Total Execution Time Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(test_types, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Requests per second comparison
    orig_rps = [original_results[t].get('requests_per_second', 0) for t in test_types]
    opt_rps = [optimized_results[t].get('requests_per_second', 0) for t in test_types]
    
    ax3.bar([i - width/2 for i in x], orig_rps, width, label='Original', alpha=0.8, color='red')
    ax3.bar([i + width/2 for i in x], opt_rps, width, label='Optimized', alpha=0.8, color='green')
    ax3.set_xlabel('Test Type')
    ax3.set_ylabel('Requests per Second')
    ax3.set_title('Throughput Comparison (RPS)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(test_types, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Performance improvement percentage
    improvements = []
    for i, test_type in enumerate(test_types):
        if orig_times[i] > 0 and opt_times[i] > 0:
            improvement = ((orig_times[i] - opt_times[i]) / orig_times[i]) * 100
            improvements.append(improvement)
        else:
            improvements.append(0)
    
    colors = ['green' if imp > 0 else 'red' for imp in improvements]
    ax4.bar(x, improvements, color=colors, alpha=0.8)
    ax4.set_xlabel('Test Type')
    ax4.set_ylabel('Improvement (%)')
    ax4.set_title('Performance Improvement Percentage')
    ax4.set_xticks(x)
    ax4.set_xticklabels(test_types, rotation=45)
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
    print("📊 Chart saved as 'performance_comparison.png'")


async def main():
    """Main performance testing function"""
    print("🔥 Cross-Mind Consensus API Performance Comparison")
    print("=" * 60)
    
    # Initialize testers
    original_tester = PerformanceTester(API_BASE_URL, API_KEY, "Original API")
    optimized_tester = PerformanceTester(OPTIMIZED_API_BASE_URL, API_KEY, "Optimized API")
    
    # Test questions subset for faster testing
    test_questions = TEST_QUESTIONS[:5]  # Use first 5 questions
    
    # Test scenarios
    test_scenarios = [
        ("Sequential", "test_sync_sequential", {}),
        ("Concurrent (3 threads)", "test_sync_concurrent", {"max_workers": 3}),
        ("Async Concurrent (3)", "test_async_concurrent", {"max_concurrent": 3}),
    ]
    
    original_results = {}
    optimized_results = {}
    
    for scenario_name, method_name, kwargs in test_scenarios:
        print(f"\n🧪 Running scenario: {scenario_name}")
        print("-" * 40)
        
        # Test original API
        try:
            if method_name == "test_async_concurrent":
                orig_result = await getattr(original_tester, method_name)(test_questions, **kwargs)
            else:
                orig_result = getattr(original_tester, method_name)(test_questions, **kwargs)
            original_results[scenario_name] = orig_result
            print_results(orig_result, f"Original API - {scenario_name}")
        except Exception as e:
            print(f"❌ Original API test failed: {e}")
            original_results[scenario_name] = {"error": str(e)}
        
        # Test optimized API
        try:
            if method_name == "test_async_concurrent":
                opt_result = await getattr(optimized_tester, method_name)(test_questions, **kwargs)
            else:
                opt_result = getattr(optimized_tester, method_name)(test_questions, **kwargs)
            optimized_results[scenario_name] = opt_result
            print_results(opt_result, f"Optimized API - {scenario_name}")
        except Exception as e:
            print(f"❌ Optimized API test failed: {e}")
            optimized_results[scenario_name] = {"error": str(e)}
        
        # Calculate improvement
        if (scenario_name in original_results and scenario_name in optimized_results and
            "avg_response_time" in original_results[scenario_name] and
            "avg_response_time" in optimized_results[scenario_name]):
            
            orig_time = original_results[scenario_name]["avg_response_time"]
            opt_time = optimized_results[scenario_name]["avg_response_time"]
            
            if orig_time > 0:
                improvement = ((orig_time - opt_time) / orig_time) * 100
                speedup = orig_time / opt_time if opt_time > 0 else float('inf')
                print(f"🚀 Performance improvement: {improvement:.1f}% ({speedup:.1f}x speedup)")
    
    # Create comparison charts
    try:
        create_comparison_chart(original_results, optimized_results)
    except Exception as e:
        print(f"⚠️ Could not create charts: {e}")
    
    # Save detailed results
    results_data = {
        "original": original_results,
        "optimized": optimized_results,
        "test_config": {
            "questions_tested": len(test_questions),
            "scenarios": [s[0] for s in test_scenarios],
            "timestamp": time.time()
        }
    }
    
    with open("performance_results.json", "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n💾 Detailed results saved to 'performance_results.json'")
    print("\n🎉 Performance comparison completed!")


if __name__ == "__main__":
    asyncio.run(main()) 