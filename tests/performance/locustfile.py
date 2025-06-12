"""
Performance Testing for Cross-Mind Consensus API using Locust
"""

import json
import random

from locust import HttpUser, between, task


class ConsensusAPIUser(HttpUser):
    """Simulated user for performance testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Called when a user starts"""
        # Check if API is healthy
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"Health check failed: {response.status_code}")

    @task(3)
    def test_consensus_basic(self):
        """Test basic consensus endpoint (weight: 3)"""
        questions = [
            "What is artificial intelligence?",
            "Explain machine learning concepts",
            "What are the benefits of cloud computing?",
            "How does blockchain technology work?",
            "What is the future of renewable energy?",
            "Explain quantum computing principles",
            "What are the best practices for software development?",
            "How can AI improve healthcare?",
            "What is the impact of automation on jobs?",
            "Explain the concept of digital transformation",
        ]

        question = random.choice(questions)

        payload = {
            "question": question,
            "method": "expert_roles",
            "max_models": 3,
            "temperature": 0.7,
        }

        with self.client.post(
            "/consensus",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "consensus_response" in data and "consensus_score" in data:
                    response.success()
                else:
                    response.failure("Missing required response fields")
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def test_batch_consensus(self):
        """Test batch consensus endpoint (weight: 1)"""
        questions = [
            "What is Python programming?",
            "Explain data structures",
            "What is agile methodology?",
        ]

        payload = {"questions": questions, "method": "expert_roles"}

        with self.client.post(
            "/consensus/batch",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "results" in data and "batch_summary" in data:
                    response.success()
                else:
                    response.failure("Missing batch response fields")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def test_models_endpoint(self):
        """Test models information endpoint (weight: 2)"""
        with self.client.get("/models", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    response.success()
                else:
                    response.failure("Missing models data")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def test_analytics_endpoint(self):
        """Test analytics endpoint (weight: 1)"""
        with self.client.get("/analytics/performance", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "timeframe" in data:
                    response.success()
                else:
                    response.failure("Missing analytics data")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(4)
    def test_health_check(self):
        """Test health check endpoint (weight: 4)"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    response.success()
                else:
                    response.failure("Missing health status")
            else:
                response.failure(f"HTTP {response.status_code}")


class StressTestUser(HttpUser):
    """High-intensity stress test user"""

    wait_time = between(0.1, 0.5)  # Very short wait times

    @task
    def stress_consensus(self):
        """Rapid-fire consensus requests"""
        payload = {
            "question": "Quick test question",
            "method": "direct_consensus",
            "max_models": 2,
        }

        self.client.post("/consensus", json=payload)


# Custom performance test scenarios
class LongRunningTestUser(HttpUser):
    """Test long-running requests"""

    wait_time = between(5, 10)

    @task
    def complex_question(self):
        """Test with complex, long questions"""
        complex_question = """
        Analyze the comprehensive impact of artificial intelligence on modern society, 
        considering economic, social, ethical, and technological perspectives. 
        Discuss both positive and negative implications, provide specific examples, 
        and suggest policy recommendations for managing AI development responsibly.
        """

        payload = {
            "question": complex_question,
            "method": "expert_roles",
            "max_models": 5,
            "temperature": 0.8,
        }

        self.client.post("/consensus", json=payload)
