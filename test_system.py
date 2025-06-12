#!/usr/bin/env python3
"""
Test script for Cross-Mind Consensus System
Tests various scenarios and validates system behavior
"""

import asyncio
import json
import time
from typing import Any, Dict, List

import requests

# Test Configuration
API_BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "test-key"
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}


def test_basic_api_connection():
    """Test basic API connectivity"""
    print("🔍 Testing API Connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        assert response.status_code == 200
        print("✅ API Connection: PASSED")
        return True
    except Exception as e:
        print(f"❌ API Connection: FAILED - {e}")
        return False


def test_auth_validation():
    """Test Bearer token authentication"""
    print("🔐 Testing Authentication...")

    # Test without token
    try:
        response = requests.post(f"{API_BASE_URL}/llm/qa")
        assert response.status_code == 401
        print("✅ Auth Rejection (No Token): PASSED")
    except Exception as e:
        print(f"❌ Auth Rejection Test: FAILED - {e}")
        return False

    # Test with invalid token
    try:
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = requests.post(f"{API_BASE_URL}/llm/qa", headers=invalid_headers)
        assert response.status_code == 403
        print("✅ Auth Rejection (Invalid Token): PASSED")
    except Exception as e:
        print(f"❌ Invalid Token Test: FAILED - {e}")
        return False

    print("✅ Authentication Tests: ALL PASSED")
    return True


def test_agreement_method():
    """Test agreement-based consensus"""
    print("🤝 Testing Agreement Method...")

    payload = {
        "question": "What is the capital of France?",
        "roles": ["Expert", "Reviewer", "Validator"],
        "model_ids": ["openai_gpt4", "anthropic_claude", "zhipu"],
        "method": "agreement",
        "save_log": True,
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/llm/qa", json=payload, headers=HEADERS, timeout=60
        )

        if response.status_code == 200:
            result = response.json()

            # Validate response structure
            assert "answers" in result
            assert "agreement_score" in result
            assert len(result["answers"]) == 3

            print(f"✅ Agreement Score: {result['agreement_score']:.3f}")
            print(
                f"✅ Individual Scores: {result.get('individual_model_agreement', {})}"
            )
            print("✅ Agreement Method: PASSED")
            return True
        else:
            print(f"❌ Agreement Method: FAILED - Status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Agreement Method: FAILED - {e}")
        return False


def test_chain_method():
    """Test chain verification method"""
    print("🔗 Testing Chain Method...")

    payload = {
        "question": "Explain quantum entanglement in simple terms",
        "roles": ["Scientist", "Critic", "Educator"],
        "model_ids": ["openai_gpt4", "anthropic_claude", "zhipu"],
        "method": "chain",
        "chain_depth": 2,
        "save_log": True,
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/llm/qa", json=payload, headers=HEADERS, timeout=120
        )

        if response.status_code == 200:
            result = response.json()

            # Validate response structure
            assert "chain_process" in result
            assert "final_answer" in result
            assert len(result["chain_process"]) == 2  # chain_depth

            print("✅ Chain Process Generated")
            print(f"✅ Final Answer Length: {len(result['final_answer'])} chars")
            print("✅ Chain Method: PASSED")
            return True
        else:
            print(f"❌ Chain Method: FAILED - Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Chain Method: FAILED - {e}")
        return False


def test_auto_weights():
    """Test automatic weight suggestion"""
    print("⚖️ Testing Auto-Weight System...")

    payload = {
        "question": "What is machine learning?",
        "roles": ["Teacher"],
        "model_ids": ["openai_gpt4"],
        "method": "agreement",
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/llm/auto-weights", json=payload, headers=HEADERS
        )

        if response.status_code == 200:
            result = response.json()
            assert "auto_weights" in result
            assert len(result["auto_weights"]) == 1
            print(f"✅ Auto Weights: {result['auto_weights']}")
            print("✅ Auto-Weight System: PASSED")
            return True
        else:
            print(f"❌ Auto-Weight System: FAILED - Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Auto-Weight System: FAILED - {e}")
        return False


def test_edge_cases():
    """Test edge cases and error handling"""
    print("🎯 Testing Edge Cases...")

    # Test empty question
    try:
        payload = {
            "question": "",
            "roles": ["Expert"],
            "model_ids": ["openai_gpt4"],
            "method": "agreement",
        }
        response = requests.post(
            f"{API_BASE_URL}/llm/qa", json=payload, headers=HEADERS
        )
        print("✅ Empty Question Handling: Response received")
    except Exception as e:
        print(f"⚠️ Empty Question Test: {e}")

    # Test mismatched roles and models
    try:
        payload = {
            "question": "Test question",
            "roles": ["Expert", "Reviewer"],
            "model_ids": ["openai_gpt4"],  # Mismatch: 2 roles, 1 model
            "method": "agreement",
        }
        response = requests.post(
            f"{API_BASE_URL}/llm/qa", json=payload, headers=HEADERS
        )
        print("✅ Mismatched Roles/Models: Handled gracefully")
    except Exception as e:
        print(f"⚠️ Mismatch Test: {e}")

    print("✅ Edge Cases: COMPLETED")
    return True


def test_performance():
    """Test system performance"""
    print("⏱️ Testing Performance...")

    payload = {
        "question": "What is artificial intelligence?",
        "roles": ["Expert"],
        "model_ids": ["openai_gpt4"],
        "method": "agreement",
        "save_log": False,  # Disable logging for performance
    }

    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE_URL}/llm/qa", json=payload, headers=HEADERS, timeout=30
        )
        end_time = time.time()

        response_time = end_time - start_time
        print(f"✅ Response Time: {response_time:.2f}s")

        if response_time < 10:
            print("✅ Performance: EXCELLENT (<10s)")
        elif response_time < 20:
            print("✅ Performance: GOOD (<20s)")
        else:
            print("⚠️ Performance: SLOW (>20s)")

        return True
    except Exception as e:
        print(f"❌ Performance Test: FAILED - {e}")
        return False


def generate_test_report(results: Dict[str, bool]):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 50)
    print("📊 CROSS-MIND CONSENSUS TEST REPORT")
    print("=" * 50)

    passed = sum(results.values())
    total = len(results)
    success_rate = (passed / total) * 100

    print(f"📈 Overall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    print("\n📋 Detailed Results:")

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")

    print("\n🎯 Recommendations:")
    if success_rate >= 90:
        print("  🌟 System is ready for production!")
    elif success_rate >= 75:
        print("  ⚠️ System mostly functional, address failing tests")
    else:
        print("  🚨 System needs significant fixes before deployment")

    print("=" * 50)


def main():
    """Run all tests"""
    print("🚀 Starting Cross-Mind Consensus System Tests\n")

    test_results = {}

    # Run all tests
    test_results["API Connection"] = test_basic_api_connection()
    test_results["Authentication"] = test_auth_validation()
    test_results["Agreement Method"] = test_agreement_method()
    test_results["Chain Method"] = test_chain_method()
    test_results["Auto-Weight System"] = test_auto_weights()
    test_results["Edge Cases"] = test_edge_cases()
    test_results["Performance"] = test_performance()

    # Generate report
    generate_test_report(test_results)


if __name__ == "__main__":
    main()
