"""
Real LLM Client for Cross-Mind Consensus
Integrates multiple AI providers including working GLM-4-AIR
"""

import os
import asyncio
import httpx
import json
import time
from typing import Dict, Any, List, Optional
from zhipu_glm4_air import ZhipuGLM4AirClient

class RealLLMClient:
    def __init__(self):
        self.zhipu_client = ZhipuGLM4AirClient()
        self.timeout = 30.0
        
    async def call_model(self, model_id: str, question: str, temperature: float = 0.7) -> Dict[str, Any]:
        """Call the appropriate model based on model_id"""
        start_time = time.time()
        
        try:
            if model_id.startswith("zhipuai"):
                result = await self._call_zhipu_model(model_id, question, temperature)
            elif model_id.startswith("openai"):
                result = await self._call_openai_model(model_id, question, temperature)
            elif model_id.startswith("anthropic"):
                result = await self._call_anthropic_model(model_id, question, temperature)
            elif model_id.startswith("google"):
                result = await self._call_google_model(model_id, question, temperature)
            else:
                result = await self._get_fallback_response(model_id, question)
                
            # Add timing information
            result["response_time"] = time.time() - start_time
            return result
            
        except Exception as e:
            return {
                "model": model_id,
                "error": f"Exception: {str(e)}",
                "success": False,
                "response_time": time.time() - start_time
            }
    
    async def _call_zhipu_model(self, model_id: str, question: str, temperature: float) -> Dict[str, Any]:
        """Call ZhipuAI models (GLM-4-AIR working)"""
        if model_id == "zhipuai_glm4_air":
            result = await self.zhipu_client.call_glm4_air(question, temperature)
            if result.get("success"):
                return {
                    "model": model_id,
                    "response": result["response"],
                    "confidence": result.get("confidence", 0.85),
                    "success": True,
                    "provider": "zhipuai"
                }
            else:
                return {
                    "model": model_id,
                    "error": result.get("error", "Unknown error"),
                    "success": False,
                    "provider": "zhipuai"
                }
        else:
            # Other ZhipuAI models (GLM-4, GLM-3-turbo) - may be out of credits
            return await self._get_fallback_response(model_id, question)
    
    async def _call_openai_model(self, model_id: str, question: str, temperature: float) -> Dict[str, Any]:
        """Call OpenAI models"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-your-"):
            return await self._get_fallback_response(model_id, question)
        
        model_map = {
            "openai_gpt4": "gpt-4",
            "openai_gpt4_turbo": "gpt-4-turbo",
            "openai_gpt35_turbo": "gpt-3.5-turbo"
        }
        
        model_name = model_map.get(model_id, "gpt-3.5-turbo")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 500,
            "temperature": temperature
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "model": model_id,
                        "response": result["choices"][0]["message"]["content"],
                        "confidence": 0.9,
                        "success": True,
                        "provider": "openai"
                    }
                else:
                    return await self._get_fallback_response(model_id, question)
        except Exception:
            return await self._get_fallback_response(model_id, question)
    
    async def _call_anthropic_model(self, model_id: str, question: str, temperature: float) -> Dict[str, Any]:
        """Call Anthropic models"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key.startswith("sk-ant-"):
            return await self._get_fallback_response(model_id, question)
        
        model_map = {
            "anthropic_claude3_opus": "claude-3-opus-20240229",
            "anthropic_claude3_sonnet": "claude-3-sonnet-20240229",
            "anthropic_claude3_haiku": "claude-3-haiku-20240307"
        }
        
        model_name = model_map.get(model_id, "claude-3-sonnet-20240229")
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model_name,
            "max_tokens": 500,
            "temperature": temperature,
            "messages": [{"role": "user", "content": question}]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "model": model_id,
                        "response": result["content"][0]["text"],
                        "confidence": 0.88,
                        "success": True,
                        "provider": "anthropic"
                    }
                else:
                    return await self._get_fallback_response(model_id, question)
        except Exception:
            return await self._get_fallback_response(model_id, question)
    
    async def _call_google_model(self, model_id: str, question: str, temperature: float) -> Dict[str, Any]:
        """Call Google models"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key.startswith("AIza"):
            return await self._get_fallback_response(model_id, question)
        
        # Google Gemini API implementation would go here
        return await self._get_fallback_response(model_id, question)
    
    async def _get_fallback_response(self, model_id: str, question: str) -> Dict[str, Any]:
        """Generate intelligent fallback response when API is not available"""
        # Import the rule-based system from our working implementation
        from free_llm_integration import FreeLLMClient
        
        free_client = FreeLLMClient()
        result = free_client.get_rule_based_response(question)
        
        return {
            "model": f"{model_id} (fallback)",
            "response": result["response"],
            "confidence": result["confidence"],
            "success": True,
            "provider": "fallback",
            "note": "Using intelligent rule-based response due to API unavailability"
        }

# Test function
async def test_real_llm_client():
    """Test the real LLM client"""
    client = RealLLMClient()
    
    test_questions = [
        "What is 2+2?",
        "2+2等于多少？",
        "Explain Python programming language briefly",
        "What are the benefits of renewable energy?"
    ]
    
    test_models = [
        "zhipuai_glm4_air",
        "openai_gpt4",
        "anthropic_claude3_sonnet",
        "google_gemini_pro"
    ]
    
    print("🧪 测试真实LLM客户端...")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\n❓ 问题: {question}")
        print("-" * 40)
        
        for model_id in test_models:
            result = await client.call_model(model_id, question)
            
            if result.get("success"):
                response = result["response"][:100] + "..." if len(result["response"]) > 100 else result["response"]
                print(f"✅ {model_id}: {response}")
                print(f"   信心度: {result.get('confidence', 'N/A')}, 响应时间: {result.get('response_time', 0):.2f}s")
                if result.get("note"):
                    print(f"   注意: {result['note']}")
            else:
                print(f"❌ {model_id}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_real_llm_client()) 