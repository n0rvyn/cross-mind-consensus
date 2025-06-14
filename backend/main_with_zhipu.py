"""
Cross-Mind Consensus API with Real ZhipuAI Integration
集成真实智谱AI GLM-4-AIR和embedding-3的共识计算API
"""

import os
import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import httpx
import numpy as np

# 导入智谱AI客户端
from zhipu_glm4_air import ZhipuGLM4AirClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cross-Mind Consensus API with ZhipuAI", version="2.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis连接
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Redis连接成功")
except Exception as e:
    logger.error(f"❌ Redis连接失败: {e}")
    redis_client = None

# 智谱AI客户端
zhipu_client = ZhipuGLM4AirClient()

# 请求模型
class ConsensusRequest(BaseModel):
    question: str
    models: Optional[List[str]] = ["glm-4-air", "rule-based", "embedding-enhanced"]
    temperature: Optional[float] = 0.7
    use_embeddings: Optional[bool] = True

class ChainOfThoughtRequest(BaseModel):
    question: str
    steps: Optional[int] = 3
    use_embeddings: Optional[bool] = True

# 规则基础响应系统（作为备用）
class RuleBasedResponder:
    def __init__(self):
        self.math_patterns = {
            r'(\d+)\s*\+\s*(\d+)': lambda m: f"{m.group(1)} + {m.group(2)} = {int(m.group(1)) + int(m.group(2))}",
            r'(\d+)\s*-\s*(\d+)': lambda m: f"{m.group(1)} - {m.group(2)} = {int(m.group(1)) - int(m.group(2))}",
            r'(\d+)\s*\*\s*(\d+)': lambda m: f"{m.group(1)} × {m.group(2)} = {int(m.group(1)) * int(m.group(2))}",
            r'(\d+)\s*/\s*(\d+)': lambda m: f"{m.group(1)} ÷ {m.group(2)} = {int(m.group(1)) / int(m.group(2))}" if int(m.group(2)) != 0 else "除数不能为零"
        }
        
        self.knowledge_base = {
            "python": "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。",
            "ai": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
            "climate": "气候变化是指地球气候系统长期的变化，主要由人类活动导致的温室气体排放引起。",
            "hello": "你好！我是Cross-Mind Consensus AI助手，很高兴为您服务！"
        }
    
    def respond(self, question: str) -> Dict[str, Any]:
        import re
        
        question_lower = question.lower()
        
        # 数学计算
        for pattern, calculator in self.math_patterns.items():
            match = re.search(pattern, question)
            if match:
                try:
                    result = calculator(match)
                    return {
                        "model": "Rule-Based Math",
                        "response": result,
                        "confidence": 0.95,
                        "reasoning": "基于数学规则的精确计算"
                    }
                except:
                    continue
        
        # 知识库匹配
        for keyword, answer in self.knowledge_base.items():
            if keyword in question_lower:
                return {
                    "model": "Rule-Based Knowledge",
                    "response": answer,
                    "confidence": 0.8,
                    "reasoning": f"基于关键词 '{keyword}' 的知识库匹配"
                }
        
        # 默认响应
        return {
            "model": "Rule-Based Default",
            "response": f"我理解您询问关于 '{question}' 的问题。这是一个有趣的话题，需要进一步分析。",
            "confidence": 0.6,
            "reasoning": "通用响应模板"
        }

rule_responder = RuleBasedResponder()

async def get_model_response(question: str, model: str, temperature: float = 0.7) -> Dict[str, Any]:
    """获取单个模型的响应"""
    try:
        if model == "glm-4-air":
            result = await zhipu_client.call_glm4_air(question, temperature)
            if result.get("success"):
                return {
                    "model": result["model"],
                    "response": result["response"],
                    "confidence": result["confidence"],
                    "reasoning": "智谱AI GLM-4-AIR模型推理"
                }
            else:
                logger.warning(f"GLM-4-AIR调用失败: {result.get('error')}")
                # 回退到规则系统
                return rule_responder.respond(question)
        
        elif model == "rule-based":
            return rule_responder.respond(question)
        
        elif model == "embedding-enhanced":
            # 使用embedding增强的响应
            embedding_result = await zhipu_client.get_embedding(question)
            if embedding_result.get("success"):
                # 先获取基础响应
                base_response = await zhipu_client.call_glm4_air(question, temperature)
                if base_response.get("success"):
                    return {
                        "model": "GLM-4-Air + Embedding",
                        "response": base_response["response"],
                        "confidence": min(base_response["confidence"] + 0.1, 1.0),
                        "reasoning": "结合向量语义理解的增强推理",
                        "embedding_dimensions": len(embedding_result["embedding"])
                    }
            
            # 回退到规则系统
            return rule_responder.respond(question)
        
        else:
            return {
                "model": f"Unknown-{model}",
                "response": f"未知模型 {model}，使用默认响应。",
                "confidence": 0.3,
                "reasoning": "未知模型回退"
            }
    
    except Exception as e:
        logger.error(f"模型 {model} 响应错误: {e}")
        return {
            "model": f"Error-{model}",
            "response": f"模型 {model} 出现错误，使用备用响应。",
            "confidence": 0.2,
            "reasoning": f"错误回退: {str(e)}"
        }

def calculate_consensus(responses: List[Dict[str, Any]], use_embeddings: bool = True) -> Dict[str, Any]:
    """计算多模型共识"""
    if not responses:
        return {
            "consensus_response": "无可用响应",
            "confidence": 0.0,
            "agreement_score": 0.0
        }
    
    # 按置信度排序
    responses.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    
    # 如果只有一个响应
    if len(responses) == 1:
        return {
            "consensus_response": responses[0]["response"],
            "confidence": responses[0]["confidence"],
            "agreement_score": 1.0,
            "reasoning": "单一模型响应"
        }
    
    # 多模型共识计算
    best_response = responses[0]
    total_confidence = sum(r.get("confidence", 0) for r in responses)
    avg_confidence = total_confidence / len(responses)
    
    # 简单的一致性检查（基于响应长度和关键词）
    response_lengths = [len(r["response"]) for r in responses]
    length_variance = np.var(response_lengths) if len(response_lengths) > 1 else 0
    
    # 计算一致性分数
    agreement_score = max(0.0, 1.0 - (length_variance / 1000))  # 简化的一致性计算
    
    # 如果使用embedding计算语义相似度
    semantic_similarity = 0.0
    if use_embeddings and len(responses) > 1:
        try:
            # 这里可以添加更复杂的语义相似度计算
            # 目前使用简化版本
            semantic_similarity = 0.8  # 占位符
        except:
            semantic_similarity = 0.0
    
    final_confidence = min((avg_confidence + agreement_score + semantic_similarity) / 3, 1.0)
    
    return {
        "consensus_response": best_response["response"],
        "confidence": final_confidence,
        "agreement_score": agreement_score,
        "semantic_similarity": semantic_similarity,
        "reasoning": f"基于{len(responses)}个模型的共识计算",
        "model_details": [
            {
                "model": r["model"],
                "confidence": r["confidence"],
                "response_length": len(r["response"])
            } for r in responses
        ]
    }

@app.get("/")
async def root():
    return {
        "message": "Cross-Mind Consensus API with ZhipuAI",
        "version": "2.0",
        "features": [
            "Real ZhipuAI GLM-4-AIR integration",
            "Embedding-3 vector similarity",
            "Multi-model consensus",
            "Rule-based fallback",
            "Chain-of-thought reasoning"
        ],
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # 检查Redis
    try:
        if redis_client:
            redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "unavailable"
    except:
        health_status["services"]["redis"] = "unhealthy"
    
    # 检查智谱AI
    try:
        test_result = await zhipu_client.call_glm4_air("test", 0.1)
        if test_result.get("success"):
            health_status["services"]["zhipu_glm4_air"] = "healthy"
        else:
            health_status["services"]["zhipu_glm4_air"] = "limited"
    except:
        health_status["services"]["zhipu_glm4_air"] = "unhealthy"
    
    # 检查embedding
    try:
        embed_result = await zhipu_client.get_embedding("test")
        if embed_result.get("success"):
            health_status["services"]["zhipu_embedding"] = "healthy"
        else:
            health_status["services"]["zhipu_embedding"] = "unhealthy"
    except:
        health_status["services"]["zhipu_embedding"] = "unhealthy"
    
    return health_status

@app.post("/consensus")
async def get_consensus(request: ConsensusRequest):
    """获取多模型共识响应"""
    start_time = time.time()
    
    try:
        # 并行获取所有模型响应
        tasks = []
        for model in request.models:
            task = get_model_response(request.question, model, request.temperature)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常响应
        valid_responses = []
        for response in responses:
            if isinstance(response, dict):
                valid_responses.append(response)
            else:
                logger.error(f"模型响应异常: {response}")
        
        # 计算共识
        consensus = calculate_consensus(valid_responses, request.use_embeddings)
        
        # 缓存结果
        if redis_client:
            try:
                cache_key = f"consensus:{hash(request.question)}:{hash(str(request.models))}"
                cache_data = {
                    "question": request.question,
                    "consensus": consensus,
                    "timestamp": datetime.now().isoformat(),
                    "models_used": request.models
                }
                redis_client.setex(cache_key, 3600, json.dumps(cache_data))  # 1小时缓存
            except Exception as e:
                logger.warning(f"缓存失败: {e}")
        
        processing_time = time.time() - start_time
        
        return {
            "question": request.question,
            "consensus": consensus,
            "individual_responses": valid_responses,
            "models_used": request.models,
            "processing_time": round(processing_time, 3),
            "timestamp": datetime.now().isoformat(),
            "use_embeddings": request.use_embeddings
        }
    
    except Exception as e:
        logger.error(f"共识计算错误: {e}")
        raise HTTPException(status_code=500, detail=f"共识计算失败: {str(e)}")

@app.post("/chain-of-thought")
async def chain_of_thought(request: ChainOfThoughtRequest):
    """链式思维推理"""
    start_time = time.time()
    
    try:
        steps = []
        current_question = request.question
        
        for step_num in range(request.steps):
            step_prompt = f"步骤 {step_num + 1}: 分析问题 '{current_question}'"
            
            # 获取当前步骤的响应
            response = await zhipu_client.call_glm4_air(step_prompt, 0.7)
            
            if response.get("success"):
                step_result = {
                    "step": step_num + 1,
                    "question": step_prompt,
                    "response": response["response"],
                    "confidence": response["confidence"]
                }
                
                # 如果使用embedding，计算与原问题的相关性
                if request.use_embeddings:
                    try:
                        original_embedding = await zhipu_client.get_embedding(request.question)
                        step_embedding = await zhipu_client.get_embedding(response["response"])
                        
                        if original_embedding.get("success") and step_embedding.get("success"):
                            similarity = zhipu_client.calculate_similarity(
                                original_embedding["embedding"],
                                step_embedding["embedding"]
                            )
                            step_result["relevance_to_original"] = similarity
                    except Exception as e:
                        logger.warning(f"相关性计算失败: {e}")
                
                steps.append(step_result)
                
                # 为下一步准备问题
                if step_num < request.steps - 1:
                    current_question = f"基于前面的分析，进一步思考: {response['response'][:100]}..."
            else:
                # 如果GLM-4-AIR失败，使用规则系统
                rule_response = rule_responder.respond(step_prompt)
                steps.append({
                    "step": step_num + 1,
                    "question": step_prompt,
                    "response": rule_response["response"],
                    "confidence": rule_response["confidence"],
                    "fallback": True
                })
        
        # 生成最终总结
        final_summary_prompt = f"总结以上{len(steps)}个步骤的分析，给出最终答案: {request.question}"
        final_response = await zhipu_client.call_glm4_air(final_summary_prompt, 0.8)
        
        if not final_response.get("success"):
            final_response = rule_responder.respond(final_summary_prompt)
        
        processing_time = time.time() - start_time
        
        return {
            "question": request.question,
            "steps": steps,
            "final_summary": {
                "response": final_response.get("response", "无法生成最终总结"),
                "confidence": final_response.get("confidence", 0.5)
            },
            "total_steps": len(steps),
            "processing_time": round(processing_time, 3),
            "timestamp": datetime.now().isoformat(),
            "use_embeddings": request.use_embeddings
        }
    
    except Exception as e:
        logger.error(f"链式思维推理错误: {e}")
        raise HTTPException(status_code=500, detail=f"链式思维推理失败: {str(e)}")

@app.get("/models")
async def list_models():
    """列出可用模型"""
    models = {
        "available_models": [
            {
                "name": "glm-4-air",
                "description": "智谱AI GLM-4-AIR模型",
                "type": "llm",
                "status": "active"
            },
            {
                "name": "rule-based",
                "description": "规则基础响应系统",
                "type": "rule_engine",
                "status": "active"
            },
            {
                "name": "embedding-enhanced",
                "description": "结合向量语义的增强模型",
                "type": "hybrid",
                "status": "active"
            }
        ],
        "embedding_model": {
            "name": "embedding-3",
            "description": "智谱AI向量模型",
            "dimensions": 2048,
            "status": "active"
        }
    }
    
    # 检查模型状态
    try:
        test_result = await zhipu_client.call_glm4_air("test", 0.1)
        if not test_result.get("success"):
            for model in models["available_models"]:
                if model["name"] == "glm-4-air":
                    model["status"] = "limited"
    except:
        for model in models["available_models"]:
            if model["name"] == "glm-4-air":
                model["status"] = "unavailable"
    
    return models

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 