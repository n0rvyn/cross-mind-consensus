"""
Free LLM Integration for Cross-Mind Consensus API
Uses free/open APIs for testing purposes
"""

import asyncio
import httpx
import json
from typing import Dict, Any

class FreeLLMClient:
    """Client for free LLM APIs"""
    
    async def call_ollama_local(self, question: str) -> Dict[str, Any]:
        """Call local Ollama API (if running)"""
        try:
            data = {
                "model": "llama2",
                "prompt": question,
                "stream": False
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "model": "Llama2 (Local)",
                        "response": result.get("response", "No response"),
                        "confidence": 0.8,
                        "success": True
                    }
                else:
                    return {
                        "model": "Llama2 (Local)",
                        "error": f"API error: {response.status_code}",
                        "success": False
                    }
        except Exception as e:
            return {
                "model": "Llama2 (Local)",
                "error": f"Ollama not running: {str(e)}",
                "success": False
            }
    
    async def call_huggingface_free(self, question: str) -> Dict[str, Any]:
        """Call Hugging Face Inference API (free tier)"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": question,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.7
                }
            }
            
            # Using a free model from Hugging Face
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return {
                            "model": "DialoGPT (HuggingFace)",
                            "response": result[0].get("generated_text", question),
                            "confidence": 0.7,
                            "success": True
                        }
                    else:
                        return {
                            "model": "DialoGPT (HuggingFace)",
                            "response": "Model is loading, please try again later",
                            "confidence": 0.5,
                            "success": True
                        }
                else:
                    return {
                        "model": "DialoGPT (HuggingFace)",
                        "error": f"API error: {response.status_code}",
                        "success": False
                    }
        except Exception as e:
            return {
                "model": "DialoGPT (HuggingFace)",
                "error": str(e),
                "success": False
            }
    
    def get_rule_based_response(self, question: str) -> Dict[str, Any]:
        """Rule-based response for common questions"""
        question_lower = question.lower()
        
        # Math questions
        if "2+2" in question_lower or "2 + 2" in question_lower:
            return {
                "model": "Rule-Based Math",
                "response": "2 + 2 = 4. This is a basic arithmetic operation where we add two units to two units, resulting in four units.",
                "confidence": 1.0,
                "success": True
            }
        
        # Simple greetings
        if any(word in question_lower for word in ["hello", "hi", "hey", "你好"]):
            return {
                "model": "Rule-Based Greeting",
                "response": "Hello! I'm a rule-based response system. How can I help you today?",
                "confidence": 0.9,
                "success": True
            }
        
        # Climate change questions
        if "climate change" in question_lower:
            return {
                "model": "Rule-Based Climate",
                "response": "Climate change refers to long-term shifts in global temperatures and weather patterns. Key mitigation strategies include renewable energy adoption, energy efficiency improvements, sustainable transportation, and carbon pricing mechanisms.",
                "confidence": 0.8,
                "success": True
            }
        
        # Programming questions
        if any(word in question_lower for word in ["programming", "python", "javascript", "coding"]):
            return {
                "model": "Rule-Based Programming",
                "response": "For programming questions, I recommend starting with Python for beginners due to its readable syntax and extensive libraries. Key concepts include variables, functions, loops, and data structures.",
                "confidence": 0.8,
                "success": True
            }
        
        # Default response
        return {
            "model": "Rule-Based General",
            "response": f"I understand you're asking about '{question}'. This appears to be a complex topic that would benefit from expert analysis considering multiple perspectives and evidence-based approaches.",
            "confidence": 0.6,
            "success": True
        }

async def test_free_llm():
    """Test free LLM integration"""
    client = FreeLLMClient()
    
    questions = [
        "What is 2+2?",
        "Hello, how are you?",
        "What are the benefits of renewable energy?",
        "What programming language should I learn first?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 50)
        
        # Test rule-based response (always works)
        rule_response = client.get_rule_based_response(question)
        print(f"Rule-Based: {rule_response}")
        
        # Test Ollama (if available)
        ollama_response = await client.call_ollama_local(question)
        print(f"Ollama: {ollama_response}")
        
        # Test HuggingFace (free but may be slow)
        hf_response = await client.call_huggingface_free(question)
        print(f"HuggingFace: {hf_response}")

if __name__ == "__main__":
    asyncio.run(test_free_llm()) 