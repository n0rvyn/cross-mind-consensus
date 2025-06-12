"""
Comprehensive Test Suite for Cross-Mind Consensus API (FIXED)
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

# Common headers for authenticated requests
AUTH_HEADERS = {"Authorization": "Bearer test-key"}

# Common request payload structure
BASIC_QA_REQUEST = {
    "question": "What is machine learning?",
    "roles": ["Expert"],
    "model_ids": ["openai_gpt4", "anthropic_claude"],
    "method": "agreement"
}


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


class TestQAEndpoint:
    """Test QA endpoints"""

    @patch("backend.main.call_llm")
    def test_qa_basic_request(self, mock_call_llm, mock_redis):
        """Test basic QA request"""
        mock_call_llm.return_value = "Test response"

        response = client.post(
            "/llm/qa", 
            json=BASIC_QA_REQUEST,
            headers=AUTH_HEADERS
        )

        assert response.status_code == 200
        data = response.json()

        assert "final_answer" in data
        assert "consensus_score" in data
        assert "individual_answers" in data
        assert isinstance(data["consensus_score"], float)
        assert 0 <= data["consensus_score"] <= 1

    @patch("backend.main.call_llm")
    def test_qa_with_chain_method(self, mock_call_llm, mock_redis):
        """Test QA with chain method"""
        mock_call_llm.return_value = "Test response"

        request_data = BASIC_QA_REQUEST.copy()
        request_data["method"] = "chain"
        request_data["chain_depth"] = 2

        response = client.post(
            "/llm/qa",
            json=request_data,
            headers=AUTH_HEADERS
        )

        assert response.status_code == 200
        data = response.json()
        assert "method" in data
        assert data["method"] == "chain"

    def test_qa_empty_question(self):
        """Test QA with empty question"""
        request_data = BASIC_QA_REQUEST.copy()
        request_data["question"] = ""

        response = client.post(
            "/llm/qa", 
            json=request_data,
            headers=AUTH_HEADERS
        )

        assert response.status_code == 422  # Validation error

    def test_qa_missing_question(self):
        """Test QA without question field"""
        request_data = BASIC_QA_REQUEST.copy()
        del request_data["question"]

        response = client.post(
            "/llm/qa", 
            json=request_data,
            headers=AUTH_HEADERS
        )

        assert response.status_code == 422  # Validation error

    def test_qa_unauthorized(self):
        """Test QA without authentication"""
        response = client.post("/llm/qa", json=BASIC_QA_REQUEST)

        assert response.status_code == 401


class TestBatchEndpoint:
    """Test batch processing endpoints"""

    @patch("backend.main.call_llm")
    def test_batch_qa_success(self, mock_call_llm, mock_redis):
        """Test successful batch QA"""
        mock_call_llm.return_value = "Test response"

        batch_request = {
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
        }

        response = client.post(
            "/llm/batch", 
            json=batch_request,
            headers=AUTH_HEADERS
        )

        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert "total_requests" in data
        assert len(data["results"]) == 2
        assert data["total_requests"] == 2

    def test_batch_qa_empty_list(self):
        """Test batch QA with empty request list"""
        response = client.post(
            "/llm/batch", 
            json={"requests": []},
            headers=AUTH_HEADERS
        )

        assert response.status_code == 400

    def test_batch_qa_too_many_requests(self):
        """Test batch QA with too many requests"""
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
            headers=AUTH_HEADERS
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

    def test_analytics_summary(self):
        """Test analytics summary"""
        response = client.get(
            "/analytics/summary",
            headers=AUTH_HEADERS
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_queries" in data

    def test_analytics_trends(self):
        """Test analytics trends"""
        response = client.get(
            "/analytics/trends?days=7",
            headers=AUTH_HEADERS
        )

        assert response.status_code == 200


class TestAuthentication:
    """Test authentication"""

    def test_api_key_required(self):
        """Test that API key is required for protected endpoints"""
        response = client.post("/llm/qa", json=BASIC_QA_REQUEST)
        assert response.status_code == 401

    def test_invalid_api_key(self):
        """Test invalid API key"""
        response = client.post(
            "/llm/qa", 
            json=BASIC_QA_REQUEST,
            headers={"Authorization": "Bearer invalid-key"}
        )
        assert response.status_code == 403


class TestErrorHandling:
    """Test error handling"""

    @patch("backend.main.call_llm")
    def test_llm_failure_handling(self, mock_call_llm):
        """Test handling of LLM failures"""
        mock_call_llm.side_effect = Exception("LLM service unavailable")

        response = client.post(
            "/llm/qa",
            json=BASIC_QA_REQUEST,
            headers=AUTH_HEADERS
        )

        assert response.status_code == 500


class TestCacheEndpoints:
    """Test cache management endpoints"""

    def test_clear_cache(self):
        """Test cache clearing"""
        response = client.delete(
            "/cache",
            headers=AUTH_HEADERS
        )

        assert response.status_code == 200
        data = response.json()
        assert "success" in data


if __name__ == "__main__":
    pytest.main([__file__]) 