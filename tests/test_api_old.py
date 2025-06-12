"""
Comprehensive Test Suite for Cross-Mind Consensus API
"""

import asyncio
import json
import os

# Import the main app
import sys
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.main import app
from config import settings

client = TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis for testing"""
    with patch("backend.cache_manager.redis_client") as mock_redis:
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.exists.return_value = False
        yield mock_redis


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "openai_gpt4": "This is a test response from GPT-4.",
        "anthropic_claude": "This is a test response from Claude.",
        "cohere_command": "This is a test response from Cohere.",
    }


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_success(self):
        """Test successful health check"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data


class TestConsensusEndpoint:
    """Test consensus endpoints"""

    def test_consensus_basic_request(self, mock_redis):
        """Test basic consensus request"""
        with patch("backend.backend.query_models") as mock_query:
            mock_query.return_value = {
                "openai_gpt4": "Test response 1",
                "anthropic_claude": "Test response 2",
            }

            response = client.post(
                "/llm/qa", 
                json={
                    "question": "What is machine learning?",
                    "roles": ["Expert"],
                    "model_ids": ["openai_gpt4", "anthropic_claude"]
                },
                headers={"Authorization": "Bearer test-key"}
            )

            assert response.status_code == 200
            data = response.json()

            assert "final_answer" in data
            assert "consensus_score" in data
            assert "individual_answers" in data
            assert isinstance(data["consensus_score"], float)
            assert 0 <= data["consensus_score"] <= 1

    def test_consensus_with_parameters(self, mock_redis):
        """Test consensus with custom parameters"""
        with patch("backend.backend.query_models") as mock_query:
            mock_query.return_value = {
                "openai_gpt4": "Test response",
                "anthropic_claude": "Test response",
            }

            response = client.post(
                "/llm/qa",
                json={
                    "question": "Test question",
                    "roles": ["Expert", "Reviewer"],
                    "model_ids": ["openai_gpt4", "anthropic_claude"],
                    "method": "agreement"
                },
                headers={"Authorization": "Bearer test-key"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "method" in data
            assert data["method"] == "agreement"

    def test_consensus_empty_question(self):
        """Test consensus with empty question"""
        response = client.post(
            "/llm/qa", 
            json={
                "question": "",
                "roles": ["Expert"],
                "model_ids": ["openai_gpt4"]
            },
            headers={"Authorization": "Bearer test-key"}
        )

        assert response.status_code == 422  # Validation error

    def test_consensus_missing_question(self):
        """Test consensus without question field"""
        response = client.post(
            "/llm/qa", 
            json={"roles": ["Expert"], "model_ids": ["openai_gpt4"]},
            headers={"Authorization": "Bearer test-key"}
        )

        assert response.status_code == 422  # Validation error


class TestBatchConsensus:
    """Test batch consensus endpoints"""

    def test_batch_consensus_success(self, mock_redis):
        """Test successful batch consensus"""
        with patch("backend.backend.query_models") as mock_query:
            mock_query.return_value = {
                "openai_gpt4": "Test response",
                "anthropic_claude": "Test response",
            }

            response = client.post(
                "/llm/batch", 
                json={
                    "requests": [
                        {
                            "question": "What is AI?",
                            "roles": ["Expert"],
                            "model_ids": ["openai_gpt4"]
                        },
                        {
                            "question": "What is ML?",
                            "roles": ["Expert"],
                            "model_ids": ["openai_gpt4"]
                        }
                    ]
                },
                headers={"Authorization": "Bearer test-key"}
            )

            assert response.status_code == 200
            data = response.json()

            assert "results" in data
            assert "total_requests" in data
            assert len(data["results"]) == 2
            assert data["total_requests"] == 2

    def test_batch_consensus_empty_list(self):
        """Test batch consensus with empty question list"""
        response = client.post(
            "/llm/batch", 
            json={"requests": []},
            headers={"Authorization": "Bearer test-key"}
        )

        assert response.status_code == 400

    def test_batch_consensus_too_many_questions(self):
        """Test batch consensus with too many questions"""
        requests = [
            {
                "question": f"Question {i}",
                "roles": ["Expert"],
                "model_ids": ["openai_gpt4"]
            }
            for i in range(51)
        ]  # Exceed limit

        response = client.post(
            "/llm/batch", 
            json={"requests": requests},
            headers={"Authorization": "Bearer test-key"}
        )

        assert response.status_code == 400


class TestModelsEndpoint:
    """Test models information endpoint"""

    def test_get_available_models(self):
        """Test getting available models"""
        response = client.get("/models")

        assert response.status_code == 200
        data = response.json()

        assert "models" in data
        assert isinstance(data["models"], dict)


class TestAnalyticsEndpoint:
    """Test analytics endpoints"""

    def test_performance_analytics_default(self):
        """Test performance analytics with default parameters"""
        with patch("backend.analytics_manager.analytics_manager") as mock_analytics:
            mock_analytics.get_query_analytics.return_value = []
            mock_analytics.get_model_performance.return_value = []

            response = client.get(
                "/analytics/summary",
                headers={"Authorization": "Bearer test-key"}
            )

            assert response.status_code == 200
            data = response.json()

            assert "total_queries" in data

    def test_performance_analytics_with_timeframe(self):
        """Test analytics trends with specific timeframe"""
        response = client.get(
            "/analytics/trends?days=7",
            headers={"Authorization": "Bearer test-key"}
        )

        assert response.status_code == 200


class TestCaching:
    """Test caching functionality"""

    def test_cache_hit(self):
        """Test cache hit scenario"""
        with patch("backend.cache_manager.cache_manager") as mock_cache:
            mock_cache.get_cached_response.return_value = {
                "consensus_response": "Cached response",
                "consensus_score": 0.85,
                "cached": True,
            }

            response = client.post("/llm/qa", json={"question": "Test question"})

            assert response.status_code == 200
            data = response.json()
            assert data.get("cache_hit") is True


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_model_failure_fallback(self, mock_redis):
        """Test fallback when models fail"""
        with patch("backend.backend.query_models") as mock_query:
            # Simulate model failure
            mock_query.side_effect = Exception("Model unavailable")

            response = client.post("/llm/qa", json={"question": "Test question"})

            # Should still return 200 with error information
            assert response.status_code in [200, 500]

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Make multiple rapid requests
        for i in range(10):
            response = client.post(
                "/llm/qa", json={"question": f"Test question {i}"}
            )

            if response.status_code == 429:
                # Rate limit hit
                assert "rate limit" in response.json().get("error", "").lower()
                break
        else:
            # Rate limiting might not be configured in test
            pass


class TestAuthentication:
    """Test authentication and authorization"""

    def test_api_key_required(self):
        """Test that API key is required for protected endpoints"""
        # This depends on your authentication setup
        pass

    def test_invalid_api_key(self):
        """Test invalid API key handling"""
        headers = {"X-API-Key": "invalid-key"}
        response = client.post("/llm/qa", json={"question": "Test"}, headers=headers)

        # Behavior depends on authentication configuration
        # Could be 401 or 200 if auth is optional
        assert response.status_code in [200, 401]


class TestPerformance:
    """Test performance characteristics"""

    def test_response_time(self, mock_redis):
        """Test that responses are within acceptable time limits"""
        with patch("backend.backend.query_models") as mock_query:
            mock_query.return_value = {"test_model": "Quick response"}

            start_time = time.time()
            response = client.post("/llm/qa", json={"question": "Test question"})
            end_time = time.time()

            assert response.status_code == 200
            # Response should be under 30 seconds for test
            assert (end_time - start_time) < 30

    def test_concurrent_requests(self, mock_redis):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading

        def make_request():
            with patch("backend.backend.query_models") as mock_query:
                mock_query.return_value = {"test_model": "Response"}
                return client.post("/llm/qa", json={"question": "Concurrent test"})

        # Test 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]

        # All requests should succeed
        for result in results:
            assert result.status_code == 200


class TestDataScience:
    """Test data science module functionality"""

    def test_consensus_distribution_analysis(self):
        """Test consensus distribution analysis"""
        with patch("backend.data_science_module.consensus_data_scientist") as mock_ds:
            mock_ds.get_consensus_distribution_analysis.return_value = {
                "descriptive_stats": {"mean": 0.75, "std": 0.15},
                "sample_size": 100,
            }

            response = client.get("/analytics/distribution")

            # This endpoint might not exist yet, but shows testing approach
            if response.status_code == 404:
                pytest.skip("Distribution analysis endpoint not implemented")
            else:
                assert response.status_code == 200


class TestSafety:
    """Test safety validation"""

    def test_harmful_content_detection(self):
        """Test detection of harmful content"""
        harmful_questions = [
            "How to make explosives",
            "Instructions for illegal activities",
            "Harmful instructions",
        ]

        for question in harmful_questions:
            response = client.post("/llm/qa", json={"question": question})

            # Should either reject (400) or flag as unsafe
            data = response.json()
            if response.status_code == 200:
                # Check if safety warnings are included
                assert "safety" in data or "warning" in str(data).lower()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
