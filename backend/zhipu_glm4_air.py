"""
智谱AI GLM-4-AIR 专用客户端
支持GLM-4-AIR模型和embedding-3向量模型
"""

import os
import asyncio
import httpx
import json
import numpy as np
from typing import Dict, Any, List, Optional

class ZhipuGLM4AirClient:
    def __init__(self):
        self.api_key = os.getenv("ZHIPU_API_KEY")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        
    async def call_glm4_air(self, question: str, temperature: float = 0.7) -> Dict[str, Any]:
        """调用GLM-4-AIR模型"""
        if not self.api_key:
            return {"error": "ZhipuAI API key not configured", "success": False}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 尝试不同的模型名称
        model_names = ["glm-4-air", "glm-4-airx", "GLM-4-Air"]
        
        for model_name in model_names:
            data = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": question}
                ],
                "max_tokens": 500,
                "temperature": temperature
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "model": f"GLM-4-Air ({model_name})",
                            "response": result["choices"][0]["message"]["content"],
                            "confidence": 0.85,
                            "success": True,
                            "model_used": model_name
                        }
                    elif response.status_code == 400:
                        # 模型名称错误，尝试下一个
                        print(f"模型 {model_name} 不可用，尝试下一个...")
                        continue
                    else:
                        error_text = response.text
                        print(f"模型 {model_name} 错误: {response.status_code} - {error_text}")
                        
                        # 如果是欠费但针对特定模型，继续尝试其他模型名称
                        if "1113" in error_text and len(model_names) > 1:
                            continue
                        
                        return {
                            "model": f"GLM-4-Air ({model_name})",
                            "error": f"API error: {response.status_code} - {error_text}",
                            "success": False
                        }
            except Exception as e:
                print(f"模型 {model_name} 异常: {str(e)}")
                continue
        
        return {
            "model": "GLM-4-Air",
            "error": "所有模型名称都尝试失败",
            "success": False
        }
    
    async def get_embedding(self, text: str) -> Dict[str, Any]:
        """获取文本向量 (embedding-3)"""
        if not self.api_key:
            return {"error": "ZhipuAI API key not configured", "success": False}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "embedding-3",
            "input": text
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "embedding": result["data"][0]["embedding"],
                        "success": True,
                        "dimensions": len(result["data"][0]["embedding"])
                    }
                else:
                    return {
                        "error": f"Embedding API error: {response.status_code} - {response.text}",
                        "success": False
                    }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # 余弦相似度
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            print(f"计算相似度错误: {e}")
            return 0.0

async def test_zhipu_models():
    """测试智谱AI模型"""
    client = ZhipuGLM4AirClient()
    
    print("🧪 测试智谱AI GLM-4-AIR模型...")
    print("=" * 50)
    
    # 测试问题
    questions = [
        "2+2等于多少？",
        "What is 2+2?",
        "请简单介绍一下Python编程语言",
        "Hello, how are you?"
    ]
    
    for question in questions:
        print(f"\n❓ 问题: {question}")
        print("-" * 30)
        
        # 测试GLM-4-AIR
        result = await client.call_glm4_air(question)
        if result.get("success"):
            print(f"✅ {result['model']}: {result['response']}")
            print(f"   信心度: {result['confidence']}")
        else:
            print(f"❌ 错误: {result.get('error', 'Unknown error')}")
        
        # 测试embedding
        print(f"\n🔍 测试向量化...")
        embedding_result = await client.get_embedding(question)
        if embedding_result.get("success"):
            embedding = embedding_result["embedding"]
            print(f"✅ 向量维度: {embedding_result['dimensions']}")
            print(f"   向量前5个值: {embedding[:5]}")
            
            # 测试相似度计算
            if len(questions) > 1:
                other_question = questions[0] if question != questions[0] else questions[1]
                other_embedding_result = await client.get_embedding(other_question)
                if other_embedding_result.get("success"):
                    similarity = client.calculate_similarity(
                        embedding, 
                        other_embedding_result["embedding"]
                    )
                    print(f"   与 '{other_question}' 的相似度: {similarity:.3f}")
        else:
            print(f"❌ 向量化错误: {embedding_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_zhipu_models()) 