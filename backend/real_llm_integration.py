"""
Real LLM Integration for Cross-Mind Consensus API
This module provides actual API calls to LLM services
"""

import os
import asyncio
import httpx
import json
from typing import Dict, Any, Optional

class RealLLMClient:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.zhipu_api_key = os.getenv("ZHIPU_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
    async def call_openai(self, question: str) -> Dict[str, Any]:
        """Call OpenAI GPT-4 API"""
        if not self.openai_api_key or self.openai_api_key.startswith("sk-your"):
            return {"error": "OpenAI API key not configured"}
            
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": question}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "model": "GPT-4",
                        "response": result["choices"][0]["message"]["content"],
                        "confidence": 0.9,
                        "success": True
                    }
                else:
                    return {
                        "model": "GPT-4",
                        "error": f"API error: {response.status_code}",
                        "success": False
                    }
        except Exception as e:
            return {
                "model": "GPT-4",
                "error": str(e),
                "success": False
            }
    
    async def call_zhipu(self, question: str) -> Dict[str, Any]:
        """Call ZhipuAI GLM-4 API"""
        if not self.zhipu_api_key:
            return {"error": "ZhipuAI API key not configured"}
            
        headers = {
            "Authorization": f"Bearer {self.zhipu_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "glm-4",
            "messages": [
                {"role": "user", "content": question}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "model": "GLM-4-Air",
                        "response": result["choices"][0]["message"]["content"],
                        "confidence": 0.85,
                        "success": True
                    }
                else:
                    return {
                        "model": "GLM-4-Air", 
                        "error": f"API error: {response.status_code} - {response.text}",
                        "success": False
                    }
        except Exception as e:
            return {
                "model": "GLM-4-Air",
                "error": str(e),
                "success": False
            }
    
    async def call_anthropic(self, question: str) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        if not self.anthropic_api_key or self.anthropic_api_key.startswith("sk-ant-your"):
            return {"error": "Anthropic API key not configured"}
            
        headers = {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": question}
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "model": "Claude 3 Sonnet",
                        "response": result["content"][0]["text"],
                        "confidence": 0.88,
                        "success": True
                    }
                else:
                    return {
                        "model": "Claude 3 Sonnet",
                        "error": f"API error: {response.status_code}",
                        "success": False
                    }
        except Exception as e:
            return {
                "model": "Claude 3 Sonnet",
                "error": str(e),
                "success": False
            }

# Test function
async def test_real_llm():
    """Test real LLM integration"""
    client = RealLLMClient()
    
    question = "What is 2+2?"
    
    print("Testing real LLM integration...")
    print(f"Question: {question}")
    print("-" * 50)
    
    # Test ZhipuAI (most likely to work based on your config)
    print("Testing ZhipuAI...")
    zhipu_result = await client.call_zhipu(question)
    print(f"ZhipuAI Result: {zhipu_result}")
    print()
    
    # Test OpenAI
    print("Testing OpenAI...")
    openai_result = await client.call_openai(question)
    print(f"OpenAI Result: {openai_result}")
    print()
    
    # Test Anthropic
    print("Testing Anthropic...")
    anthropic_result = await client.call_anthropic(question)
    print(f"Anthropic Result: {anthropic_result}")

if __name__ == "__main__":
    asyncio.run(test_real_llm()) 