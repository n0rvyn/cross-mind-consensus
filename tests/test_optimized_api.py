"""
Unit tests for the optimized Cross-Mind Consensus API
Tests async functionality, concurrent model calls, caching, and security
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import the optimized API
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main_optimized import app, get_redis_client, CacheManager, DummyCache
from backend.main_optimized import call_model_async, calculate_consensus_score_optimized
from backend.main_optimized import truncate_embedding_for_log


class TestOptimizedAPI:
    """Test suite for optimized API functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch('backend.main_optimized.settings') as mock:
            mock.backend_api_keys = ["test-key-123", "another-test-key"]
            mock.allowed_origins = ["https://test.com"]
            mock.max_concurrent_requests = 5
            mock.enable_caching = True
            mock.redis_host = "localhost"
            mock.redis_port = 6379
            mock.redis_password = ""
            mock.max_embedding_log_dims = 10
            yield mock
    
    def test_health_check(self, client, mock_settings):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        assert "performance" in data
        assert data["performance"]["async_client"] == "enabled"
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Optimized" in response.json()["message"]
    
    def test_authentication_required(self, client, mock_settings):
        """Test that authentication is required"""
        response = client.post("/consensus", json={
            "question": "Test question"
        })
        assert response.status_code == 403  # No auth header
    
    def test_invalid_token(self, client, mock_settings):
        """Test invalid token rejection"""
        response = client.post("/consensus", 
            headers={"Authorization": "Bearer invalid-token"},
            json={"question": "Test question"}
        )
        assert response.status_code == 401
    
    def test_valid_token(self, client, mock_settings):
        """Test valid token acceptance"""
        with patch('backend.main_optimized.http_client') as mock_client:
            mock_client.return_value = AsyncMock()
            
            response = client.post("/consensus",
                headers={"Authorization": "Bearer test-key-123"},
                json={"question": "Test question"}
            )
            # Should not be 401 (unauthorized)
            assert response.status_code != 401


class TestAsyncFunctionality:
    """Test async functionality and concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_call_model_async(self):
        """Test async model calling"""
        mock_client = AsyncMock()
        
        result = await call_model_async(
            mock_client, 
            "Test question", 
            "test_model", 
            "expert_roles"
        )
        
        assert isinstance(result, dict)
        assert "model" in result
        assert "response" in result
        assert "confidence" in result
        assert "response_time" in result
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_concurrent_model_calls(self):
        """Test concurrent model calls performance"""
        mock_client = AsyncMock()
        
        # Test concurrent calls
        tasks = [
            call_model_async(mock_client, f"Question {i}", f"model_{i}", "expert_roles")
            for i in range(5)
        ]
        
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()
        
        # All calls should complete
        assert len(results) == 5
        for result in results:
            assert result["success"] is True
        
        # Concurrent execution should be faster than sequential
        # (This is a rough test - in real scenarios the difference would be more significant)
        assert end_time - start_time < 2.0  # Should complete quickly
    
    @pytest.mark.asyncio
    async def test_redis_client_connection(self):
        """Test Redis client connection handling"""
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_instance = AsyncMock()
            mock_redis.return_value = mock_instance
            mock_instance.ping.return_value = True
            
            client = await get_redis_client()
            assert client is not None
            mock_instance.ping.assert_called_once()


class TestCacheManager:
    """Test caching functionality"""
    
    @pytest.mark.asyncio
    async def test_cache_manager_with_redis(self):
        """Test cache manager with Redis client"""
        mock_redis = AsyncMock()
        cache = CacheManager(mock_redis)
        
        # Test set
        await cache.set("test_key", "test_value", 3600)
        mock_redis.setex.assert_called_once_with("test_key", 3600, "test_value")
        
        # Test get
        mock_redis.get.return_value = "test_value"
        result = await cache.get("test_key")
        assert result == "test_value"
        mock_redis.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_cache_manager_error_handling(self):
        """Test cache manager error handling"""
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = Exception("Redis error")
        mock_redis.setex.side_effect = Exception("Redis error")
        
        cache = CacheManager(mock_redis)
        
        # Should handle errors gracefully
        result = await cache.get("test_key")
        assert result is None
        
        # Should not raise exception
        await cache.set("test_key", "test_value")
    
    @pytest.mark.asyncio
    async def test_dummy_cache(self):
        """Test dummy cache fallback"""
        cache = DummyCache()
        
        # Should always return None for get
        result = await cache.get("test_key")
        assert result is None
        
        # Should not raise exception for set
        await cache.set("test_key", "test_value")


class TestPerformanceOptimizations:
    """Test performance optimization features"""
    
    def test_consensus_score_optimization(self):
        """Test optimized consensus score calculation"""
        responses = [
            {"confidence": 0.9, "response": "Response 1 with some content"},
            {"confidence": 0.8, "response": "Response 2 with similar content"},
            {"confidence": 0.85, "response": "Response 3 with comparable content"}
        ]
        
        score = calculate_consensus_score_optimized(responses)
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)
    
    def test_consensus_score_edge_cases(self):
        """Test consensus score with edge cases"""
        # Empty responses
        score = calculate_consensus_score_optimized([])
        assert score == 1.0
        
        # Single response
        score = calculate_consensus_score_optimized([{"confidence": 0.8, "response": "test"}])
        assert score == 1.0
    
    def test_embedding_truncation(self):
        """Test embedding truncation for logging"""
        # Small embedding
        small_embedding = [0.1, 0.2, 0.3]
        result = truncate_embedding_for_log(small_embedding, max_dims=10)
        assert "[0.1, 0.2, 0.3]" in result
        
        # Large embedding
        large_embedding = list(range(100))
        result = truncate_embedding_for_log(large_embedding, max_dims=5)
        assert "compressed:" in result
        
        # Empty embedding
        result = truncate_embedding_for_log([])
        assert result == "[]"


class TestSecurityFeatures:
    """Test security enhancements"""
    
    def test_api_key_masking(self):
        """Test API key masking functionality"""
        from src.config import Settings
        
        # Mock SecretStr
        class MockSecretStr:
            def __init__(self, value):
                self._value = value
            
            def get_secret_value(self):
                return self._value
        
        settings = Settings()
        
        # Test masking
        long_key = MockSecretStr("sk-1234567890abcdef1234567890abcdef")
        masked = settings.get_masked_api_key(long_key)
        assert masked.startswith("sk-1")
        assert masked.endswith("cdef")
        assert "****" in masked
        
        # Test short key
        short_key = MockSecretStr("short")
        masked = settings.get_masked_api_key(short_key)
        assert masked == "****"
        
        # Test empty key
        empty_key = MockSecretStr("")
        masked = settings.get_masked_api_key(empty_key)
        assert masked == "Not configured"


class TestChainOfThoughtIntegration:
    """Test Chain-of-Thought integration"""
    
    @pytest.mark.asyncio
    async def test_cot_enhancement_request(self):
        """Test CoT enhancement in consensus request"""
        with patch('backend.main_optimized.cot_enhancer') as mock_cot:
            mock_cot.enhance_response.return_value = {
                "enhanced_response": "Enhanced analysis with CoT",
                "reasoning_chain": [
                    {"step": 1, "description": "Problem analysis"},
                    {"step": 2, "description": "Solution synthesis"}
                ],
                "quality_score": 0.92,
                "enhancement_method": "chain_of_thought"
            }
            
            # This would be part of a full integration test
            # For now, just test that the mock is properly configured
            result = mock_cot.enhance_response(
                question="Test question",
                base_responses=[],
                method="chain_of_thought"
            )
            
            assert "enhanced_response" in result
            assert "reasoning_chain" in result
            assert result["quality_score"] > 0.9


@pytest.mark.slow
class TestIntegrationScenarios:
    """Integration tests that may be slower"""
    
    @pytest.mark.asyncio
    async def test_full_consensus_flow(self):
        """Test complete consensus generation flow"""
        # This would test the full flow from request to response
        # Including caching, model calls, and response generation
        pass
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self):
        """Test batch processing performance"""
        # This would test concurrent batch processing
        pass


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"]) 