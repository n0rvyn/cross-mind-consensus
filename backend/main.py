import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append("..")
try:
    from analytics_manager import QueryAnalytics, analytics_manager
    from cache_manager import cache_manager

    from config import MODEL_CONFIG, settings
except ImportError:
    # Fallback if advanced modules are not available
    settings = None
    MODEL_CONFIG = {
        "openai_gpt4": {
            "type": "openai",
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "model": "gpt-4o",
        },
    }
    cache_manager = None
    analytics_manager = None
    QueryAnalytics = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== 应用初始化 ==========
@lru_cache(maxsize=1)
def get_embedding_model():
    model_name = settings.embedding_model_name if settings else "all-MiniLM-L6-v2"
    return SentenceTransformer(model_name)


embedding_model = get_embedding_model()
app = FastAPI(
    title="Enhanced Cross-Mind Consensus API",
    description="Multi-LLM consensus and verification system with advanced features",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自动权重缓存
MODEL_HISTORY = {}


# ========== 数据结构 ==========
class ModelAnswer(BaseModel):
    model_id: str
    role: str
    content: str
    score: Optional[float] = None
    embedding: Optional[List[float]] = None
    comment: Optional[str] = None


class QARequest(BaseModel):
    question: str
    roles: List[str]
    model_ids: List[str]
    method: str  # "agreement" or "chain"
    chain_depth: int = 2
    weights: Optional[List[float]] = None
    save_log: bool = True


# ========== 鉴权 ==========
def verify_bearer(auth: str):
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required.")
    token = auth.split(" ")[1].strip()

    # Fallback API keys if settings not available
    valid_keys = settings.backend_api_keys if settings else ["test-key", "another-key"]

    if token not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid Bearer token.")
    return True


# ========== 多厂商 LLM ==========
async def call_llm(model_id, prompt):
    conf = MODEL_CONFIG.get(model_id)
    if not conf:
        return f"[ERROR] 未配置的模型：{model_id}"

    try:
        mtype = conf["type"]
        if mtype == "openai":
            client = OpenAI(api_key=conf["api_key"])
            resp = client.chat.completions.create(
                model=conf.get("model", "gpt-4o"),
                messages=[{"role": "user", "content": prompt}],
                temperature=conf.get("temperature", 0.6),
                max_tokens=conf.get("max_tokens", 512),
            )
            return resp.choices[0].message.content.strip()
        elif mtype == "anthropic":
            # 伪代码：实际需按官方文档实现
            headers = {"x-api-key": conf["api_key"]}
            data = {
                "model": conf.get("model", "claude-3-opus-20240229"),
                "max_tokens": conf.get("max_tokens", 512),
                "messages": [{"role": "user", "content": prompt}],
            }
            url = "https://api.anthropic.com/v1/messages"
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            return resp.json()["content"][0]["text"].strip()
        elif mtype == "baidu":
            # token刷新
            if not conf["access_token"]:
                resp = requests.post(
                    f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={conf['api_key']}&client_secret={conf['secret_key']}",
                    timeout=30,
                )
                resp.raise_for_status()
                access_token = resp.json().get("access_token", "")
                conf["access_token"] = access_token
            url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={conf['access_token']}"
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "disable_search": False,
            }
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json().get("result", "[ERNIE返回缺失]")
        elif mtype == "moonshot":
            # moonshot官方API示例
            url = "https://api.moonshot.cn/v1/chat/completions"
            headers = {"Authorization": f"Bearer {conf['api_key']}"}
            payload = {
                "model": conf.get("model", "moonshot-v1-8k"),
                "messages": [{"role": "user", "content": prompt}],
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            return (
                resp.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "[moonshot无内容]")
            )
        elif mtype == "zhipu":
            # 智谱GLM API
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {"Authorization": f"Bearer {conf['api_key']}"}
            payload = {
                "model": conf.get("model", "glm-4"),
                "messages": [{"role": "user", "content": prompt}],
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            return (
                resp.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "[zhipu无内容]")
            )
        else:
            return f"[ERROR] 暂不支持的模型类型：{mtype}"
    except Exception as e:
        return f"[ERROR] {model_id} 调用失败: {str(e)}"


def get_embedding(text):
    """Get text embedding with optional caching"""
    if cache_manager and settings and settings.enable_caching:
        cached = cache_manager.get_embedding(text)
        if cached:
            return cached

    embedding = embedding_model.encode(text).tolist()

    if cache_manager and settings and settings.enable_caching:
        cache_manager.set_embedding(text, embedding)

    return embedding


def agreement_score(answers: List[ModelAnswer], weights=None):
    embs = [a.embedding for a in answers]
    sim_matrix = cosine_similarity(embs)
    n = len(answers)
    if not weights:
        weights = [1.0] * n
    weighted_scores = []
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            s = sim_matrix[i][j]
            w = (weights[i] + weights[j]) / 2
            weighted_scores.append(s * w)
            count += w
    score = sum(weighted_scores) / (count if count else 1)
    return score, [
        sum(sim_matrix[i]) / (n - 1) for i in range(n)
    ]  # 返回平均得分&每个模型的平均共识度


def save_log(log: Dict[str, Any]):
    log_dir = settings.log_directory if settings else "./logs"
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"log_{now}_{uuid.uuid4().hex[:6]}.json"

    # Optionally truncate embeddings to save space
    save_embeddings = settings.save_embeddings_in_log if settings else False
    if not save_embeddings:
        for ans in log.get("answers", []):
            if ans.get("embedding"):
                ans["embedding"] = ans["embedding"][:8] + ["..."]

    try:
        with open(f"{log_dir}/{fname}", "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        logger.info(f"Log saved: {fname}")
    except Exception as e:
        logger.error(f"Failed to save log: {e}")


# ========== 权重自动调度API ==========
@app.post("/llm/auto-weights")
def auto_weights(req: QARequest, authorization: str = Header(None)):
    verify_bearer(authorization)
    model_ids = req.model_ids
    # 查历史
    prev = MODEL_HISTORY.get(req.question, {})
    # 目前采用简单"上次共识得分"法，否则默认均分
    weights = prev.get("auto_weights", [1.0] * len(model_ids))
    return {"auto_weights": weights}


# ========== 多LLM主流程 ==========
@app.post("/llm/qa")
async def multi_llm_qa(
    req: QARequest, background_tasks: BackgroundTasks, authorization: str = Header(None)
):
    verify_bearer(authorization)
    query_id = str(uuid.uuid4())
    start_time = time.time()

    # Check cache if available
    if cache_manager and settings and settings.enable_caching:
        cached_result = cache_manager.get_consensus_score(
            req.question, req.model_ids, req.roles
        )
        if cached_result:
            logger.info(f"Returning cached result for query {query_id}")
            return cached_result

    answers: List[ModelAnswer] = []
    log = {
        "query_id": query_id,
        "question": req.question,
        "roles": req.roles,
        "model_ids": req.model_ids,
        "weights": req.weights,
        "timestamp": str(datetime.now()),
        "method": req.method,
    }
    # 1. 回答与embedding
    weights = (
        req.weights
        if req.weights and len(req.weights) == len(req.model_ids)
        else [1.0] * len(req.model_ids)
    )
    for model_id, role, weight in zip(req.model_ids, req.roles, weights):
        prompt = f"你的身份是{role}。请回答如下问题：\n{req.question}"
        content = await call_llm(model_id, prompt)
        embedding = get_embedding(content)
        ans = ModelAnswer(
            model_id=model_id,
            role=role,
            content=content,
            score=weight,
            embedding=embedding,
        )
        answers.append(ans)
    log["answers"] = [a.dict() for a in answers]
    # 2. 一致性评分与动态权重建议
    if req.method == "agreement":
        score, indiv_scores = agreement_score(answers, weights)
        log["agreement_score"] = score
        log["individual_model_agreement"] = dict(zip(req.model_ids, indiv_scores))
        threshold = settings.high_consensus_threshold if settings else 0.9
        verdict = (
            "一致性高，可信" if score >= threshold else "一致性较低，建议进一步链式验证"
        )
        log["verdict"] = verdict
        # 自动调度建议：以各自平均共识分归一化为新权重
        total = sum(indiv_scores)
        auto_weights = [
            s / total if total > 0 else 1 / len(indiv_scores) for s in indiv_scores
        ]
        log["auto_weights_suggestion"] = dict(zip(req.model_ids, auto_weights))
        # 写入缓存用于下次建议
        MODEL_HISTORY[req.question] = {"auto_weights": auto_weights}
    # 3. 链式验证
    low_threshold = settings.low_consensus_threshold if settings else 0.85
    if req.method == "chain" or (req.method == "agreement" and score < low_threshold):
        chain_answers = []
        prev_answer = answers[0].content
        for i in range(req.chain_depth):
            critic_idx = (i + 1) % len(req.model_ids)
            critic_id = req.model_ids[critic_idx]
            critic_prompt = f"你是批评者，请针对下述回答进行严肃批评与完善建议：\n\n回答：{prev_answer}"
            critic_content = await call_llm(critic_id, critic_prompt)
            reviser_idx = (i + 2) % len(req.model_ids)
            reviser_id = req.model_ids[reviser_idx]
            reviser_prompt = f"你是修正者，请根据以下批评意见优化原回答，使其更科学准确。\n原回答：{prev_answer}\n批评：{critic_content}"
            revised_answer = await call_llm(reviser_id, reviser_prompt)
            chain_answers.append(
                {
                    "round": i + 1,
                    "critic_id": critic_id,
                    "critic_content": critic_content,
                    "reviser_id": reviser_id,
                    "revised_answer": revised_answer,
                }
            )
            prev_answer = revised_answer
        log["chain_process"] = chain_answers
        log["final_answer"] = prev_answer
    # 4. Cache result if available
    if cache_manager and settings and settings.enable_caching:
        cache_manager.set_consensus_score(req.question, req.model_ids, req.roles, log)

    # 5. Record analytics if available
    if analytics_manager and QueryAnalytics:
        response_time = time.time() - start_time
        analytics = QueryAnalytics(
            query_id=query_id,
            timestamp=datetime.now(),
            question=req.question,
            model_ids=req.model_ids,
            roles=req.roles,
            method=req.method,
            consensus_score=score if "score" in locals() else 0.0,
            response_time=response_time,
            success=True,
            individual_scores=(
                dict(zip(req.model_ids, indiv_scores))
                if "indiv_scores" in locals()
                else None
            ),
            chain_rounds=req.chain_depth if req.method == "chain" else None,
        )
        background_tasks.add_task(analytics_manager.record_query, analytics)

    # 6. Enhanced logging
    if req.save_log:
        save_log(log)

    logger.info(f"Query {query_id} completed successfully")
    return log


@app.get("/")
async def root():
    return {
        "message": "Enhanced Cross-Mind Consensus API v2.0",
        "features": [
            "Multi-LLM consensus verification",
            "Advanced caching system",
            "Performance analytics",
            "Real-time monitoring",
            "Enhanced error handling",
        ],
        "status": "active",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Enhanced health check with system metrics"""
    health_info = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
    }

    # Add cache statistics if available
    if cache_manager:
        health_info["cache"] = cache_manager.get_cache_stats()

    # Add analytics summary if available
    if analytics_manager:
        health_info["analytics"] = analytics_manager.get_summary_stats()

    return health_info


@app.get("/models")
async def list_models():
    """List available models and their status"""
    models_info = {}
    for model_id, config in MODEL_CONFIG.items():
        models_info[model_id] = {
            "type": config["type"],
            "model": config.get("model", "N/A"),
            "available": bool(config.get("api_key") and config["api_key"] != ""),
        }

    return {"models": models_info}


@app.get("/analytics/summary")
async def get_analytics_summary(authorization: str = Header(None)):
    """Get analytics summary"""
    verify_bearer(authorization)

    if not analytics_manager:
        raise HTTPException(status_code=503, detail="Analytics not available")

    return analytics_manager.get_summary_stats()


@app.delete("/cache")
async def clear_cache(pattern: Optional[str] = None, authorization: str = Header(None)):
    """Clear cache entries"""
    verify_bearer(authorization)

    if not cache_manager:
        raise HTTPException(status_code=503, detail="Cache not available")

    success = cache_manager.clear_cache(pattern)
    return {
        "success": success,
        "message": f"Cache cleared{' with pattern: ' + pattern if pattern else ''}",
    }
