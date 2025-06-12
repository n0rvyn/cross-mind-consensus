#!/usr/bin/env python3
"""
Enhanced Cross-Mind Consensus System with Advanced Features
- Rate limiting and caching
- WebSocket support for real-time updates
- Additional LLM providers (Cohere, Google Gemini)
- Batch processing capabilities
- Advanced analytics and performance tracking
"""

import uuid
import os
import json
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# FastAPI and web framework imports
from fastapi import FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ML and AI imports
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import httpx

# Third-party AI providers
from openai import OpenAI
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Local imports
import sys
sys.path.append('..')
from config import settings, MODEL_CONFIG
from cache_manager import cache_manager
from analytics_manager import analytics_manager, QueryAnalytics

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

# FastAPI app initialization
app = FastAPI(
    title="Enhanced Cross-Mind Consensus API",
    description="Advanced multi-LLM consensus and verification system with caching, analytics, and real-time features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global state
embedding_model = None
websocket_connections: List[WebSocket] = []
batch_queue: List[Dict] = []

# ========== Data Models ==========
class ModelAnswer(BaseModel):
    model_id: str
    role: str
    content: str
    score: Optional[float] = None
    embedding: Optional[List[float]] = None
    comment: Optional[str] = None
    response_time: Optional[float] = None

class QARequest(BaseModel):
    question: str
    roles: List[str]
    model_ids: List[str]
    method: str = Field(default="agreement", description="agreement or chain")
    chain_depth: int = Field(default=2, ge=1, le=5)
    weights: Optional[List[float]] = None
    save_log: bool = True
    use_cache: bool = True

class BatchQARequest(BaseModel):
    requests: List[QARequest] = Field(..., max_items=50)
    parallel: bool = True

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]

# ========== Initialization ==========
@app.on_event("startup")
async def startup_event():
    """Initialize application components"""
    global embedding_model
    
    try:
        embedding_model = SentenceTransformer(settings.embedding_model_name)
        logger.info("Embedding model loaded successfully")
        
        # Initialize analytics cleanup scheduler
        asyncio.create_task(periodic_cleanup())
        
        logger.info("Enhanced Cross-Mind Consensus API started successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")

async def periodic_cleanup():
    """Periodic cleanup of old analytics data"""
    while True:
        try:
            await asyncio.sleep(86400)  # Run daily
            analytics_manager.cleanup_old_data()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# ========== Authentication ==========
def verify_bearer(auth: str):
    """Verify Bearer token authentication"""
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required.")
    token = auth.split(" ")[1].strip()
    if token not in settings.backend_api_keys:
        raise HTTPException(status_code=403, detail="Invalid Bearer token.")
    return True

# ========== Enhanced LLM Providers ==========
async def call_llm(model_id: str, prompt: str) -> str:
    """Enhanced LLM calling with caching and additional providers"""
    
    # Check cache first
    if settings.enable_caching:
        cached_response = cache_manager.get_llm_response(model_id, prompt)
        if cached_response:
            return cached_response
    
    conf = MODEL_CONFIG.get(model_id)
    if not conf:
        return f"[ERROR] 未配置的模型：{model_id}"
    
    start_time = time.time()
    
    try:
        mtype = conf['type']
        response = None
        
        if mtype == "openai":
            client = OpenAI(api_key=conf["api_key"])
            resp = await asyncio.to_thread(
                client.chat.completions.create,
                model=conf.get("model", "gpt-4o"),
                messages=[{"role": "user", "content": prompt}],
                temperature=conf.get("temperature", 0.6),
                max_tokens=conf.get("max_tokens", 512)
            )
            response = resp.choices[0].message.content.strip()
            
        elif mtype == "anthropic" and ANTHROPIC_AVAILABLE:
            client = anthropic.Anthropic(api_key=conf["api_key"])
            resp = await asyncio.to_thread(
                client.messages.create,
                model=conf.get("model", "claude-3-opus-20240229"),
                max_tokens=conf.get("max_tokens", 512),
                messages=[{"role": "user", "content": prompt}]
            )
            response = resp.content[0].text.strip()
            
        elif mtype == "cohere" and COHERE_AVAILABLE:
            client = cohere.Client(conf["api_key"])
            resp = await asyncio.to_thread(
                client.generate,
                model=conf.get("model", "command"),
                prompt=prompt,
                max_tokens=conf.get("max_tokens", 512),
                temperature=conf.get("temperature", 0.6)
            )
            response = resp.generations[0].text.strip()
            
        elif mtype == "google" and GOOGLE_AVAILABLE:
            genai.configure(api_key=conf["api_key"])
            model = genai.GenerativeModel(conf.get("model", "gemini-pro"))
            resp = await asyncio.to_thread(model.generate_content, prompt)
            response = resp.text.strip()
            
        elif mtype == "baidu":
            # Baidu ERNIE implementation
            async with httpx.AsyncClient() as client:
                if not conf["access_token"]:
                    # Get access token
                    token_resp = await client.post(
                        f"https://aip.baidubce.com/oauth/2.0/token",
                        params={
                            "grant_type": "client_credentials",
                            "client_id": conf['api_key'],
                            "client_secret": conf['secret_key']
                        },
                        timeout=30
                    )
                    conf["access_token"] = token_resp.json().get("access_token", "")
                
                # Call ERNIE API
                ernie_resp = await client.post(
                    f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
                    params={"access_token": conf["access_token"]},
                    json={"messages": [{"role": "user", "content": prompt}]},
                    timeout=30
                )
                response = ernie_resp.json().get("result", "[ERNIE返回缺失]")
                
        elif mtype in ["moonshot", "zhipu"]:
            # OpenAI-compatible APIs
            async with httpx.AsyncClient() as client:
                api_urls = {
                    "moonshot": "https://api.moonshot.cn/v1/chat/completions",
                    "zhipu": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                }
                
                resp = await client.post(
                    api_urls[mtype],
                    headers={"Authorization": f"Bearer {conf['api_key']}"},
                    json={
                        "model": conf.get("model"),
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": conf.get("temperature", 0.6),
                        "max_tokens": conf.get("max_tokens", 512)
                    },
                    timeout=30
                )
                response = resp.json().get("choices", [{}])[0].get("message", {}).get("content", f"[{mtype}无内容]")
        
        else:
            response = f"[ERROR] 暂不支持的模型类型：{mtype}"
        
        # Cache successful response
        if response and not response.startswith("[ERROR]") and settings.enable_caching:
            cache_manager.set_llm_response(model_id, prompt, response)
        
        return response
        
    except Exception as e:
        error_msg = f"[ERROR] {model_id} 调用失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

def get_embedding(text: str) -> List[float]:
    """Get text embedding with caching"""
    if settings.enable_caching:
        cached_embedding = cache_manager.get_embedding(text)
        if cached_embedding:
            return cached_embedding
    
    embedding = embedding_model.encode(text).tolist()
    
    if settings.enable_caching:
        cache_manager.set_embedding(text, embedding)
    
    return embedding

def agreement_score(answers: List[ModelAnswer], weights=None):
    """Calculate consensus score with enhanced analytics"""
    embs = [a.embedding for a in answers]
    sim_matrix = cosine_similarity(embs)
    n = len(answers)
    
    if not weights:
        weights = [1.0] * n
    
    weighted_scores = []
    count = 0
    
    for i in range(n):
        for j in range(i+1, n):
            s = sim_matrix[i][j]
            w = (weights[i] + weights[j]) / 2
            weighted_scores.append(s * w)
            count += w
    
    score = sum(weighted_scores) / (count if count else 1)
    individual_scores = [sum(sim_matrix[i]) / (n - 1) for i in range(n)]
    
    return score, individual_scores

# ========== WebSocket Management ==========
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Send heartbeat
            await asyncio.sleep(settings.websocket_heartbeat_interval)
            await websocket.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }))
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    message_str = json.dumps(message)
    disconnected = []
    
    for websocket in websocket_connections:
        try:
            await websocket.send_text(message_str)
        except Exception:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        websocket_connections.remove(ws)

# ========== Enhanced API Endpoints ==========
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Enhanced Cross-Mind Consensus API v2.0",
        "features": [
            "Multi-LLM consensus verification",
            "Real-time WebSocket updates",
            "Advanced caching with Redis",
            "Performance analytics",
            "Rate limiting",
            "Batch processing"
        ],
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    cache_stats = cache_manager.get_cache_stats()
    summary_stats = analytics_manager.get_summary_stats()
    
    return {
        "status": "healthy",
        "cache": cache_stats,
        "analytics": summary_stats,
        "websocket_connections": len(websocket_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models")
async def list_models():
    """List available models and their configurations"""
    models_info = {}
    for model_id, config in MODEL_CONFIG.items():
        models_info[model_id] = {
            "type": config["type"],
            "model": config.get("model", "N/A"),
            "available": bool(config.get("api_key"))
        }
    
    return {"models": models_info}

@app.post("/llm/qa")
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def multi_llm_qa(
    request: Request,
    req: QARequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None)
):
    """Enhanced multi-LLM Q&A with comprehensive features"""
    verify_bearer(authorization)
    
    query_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Check cache for similar queries
        cached_result = None
        if req.use_cache:
            cached_result = cache_manager.get_consensus_score(
                req.question, req.model_ids, req.roles
            )
            if cached_result:
                # Broadcast cached result
                await broadcast_to_websockets({
                    "type": "query_completed",
                    "query_id": query_id,
                    "cached": True,
                    "result": cached_result
                })
                return cached_result
        
        # Broadcast query start
        await broadcast_to_websockets({
            "type": "query_started",
            "query_id": query_id,
            "question": req.question,
            "models": req.model_ids
        })
        
        # Process answers
        answers: List[ModelAnswer] = []
        weights = req.weights if req.weights and len(req.weights) == len(req.model_ids) else [1.0] * len(req.model_ids)
        
        # Process models in parallel for better performance
        tasks = []
        for model_id, role, weight in zip(req.model_ids, req.roles, weights):
            prompt = f"你的身份是{role}。请回答如下问题：\n{req.question}"
            tasks.append(call_llm(model_id, prompt))
        
        model_responses = await asyncio.gather(*tasks)
        
        for i, (model_id, role, weight, content) in enumerate(zip(req.model_ids, req.roles, weights, model_responses)):
            embedding = get_embedding(content)
            ans = ModelAnswer(
                model_id=model_id,
                role=role,
                content=content,
                score=weight,
                embedding=embedding
            )
            answers.append(ans)
        
        # Calculate consensus
        consensus_score, individual_scores = agreement_score(answers, weights)
        
        # Prepare result
        result = {
            "query_id": query_id,
            "question": req.question,
            "answers": [ans.dict() for ans in answers],
            "consensus_score": consensus_score,
            "individual_scores": dict(zip(req.model_ids, individual_scores)),
            "method": req.method,
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine verdict
        if consensus_score >= settings.high_consensus_threshold:
            result["verdict"] = "一致性高，可信"
        else:
            result["verdict"] = "一致性较低，建议进一步链式验证"
        
        # Chain verification if needed
        if req.method == "chain" or (req.method == "agreement" and consensus_score < settings.low_consensus_threshold):
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
                
                chain_answers.append({
                    "round": i + 1,
                    "critic_id": critic_id,
                    "critic_content": critic_content,
                    "reviser_id": reviser_id,
                    "revised_answer": revised_answer
                })
                prev_answer = revised_answer
            
            result["chain_process"] = chain_answers
            result["final_answer"] = prev_answer
        
        # Cache result
        if req.use_cache:
            cache_manager.set_consensus_score(req.question, req.model_ids, req.roles, result)
        
        # Record analytics
        response_time = time.time() - start_time
        analytics = QueryAnalytics(
            query_id=query_id,
            timestamp=datetime.now(),
            question=req.question,
            model_ids=req.model_ids,
            roles=req.roles,
            method=req.method,
            consensus_score=consensus_score,
            response_time=response_time,
            success=True,
            individual_scores=dict(zip(req.model_ids, individual_scores)),
            chain_rounds=req.chain_depth if req.method == "chain" else None
        )
        background_tasks.add_task(analytics_manager.record_query, analytics)
        
        # Broadcast completion
        await broadcast_to_websockets({
            "type": "query_completed",
            "query_id": query_id,
            "consensus_score": consensus_score,
            "response_time": response_time
        })
        
        return result
        
    except Exception as e:
        error_msg = f"Query processing failed: {str(e)}"
        logger.error(error_msg)
        
        # Record failed analytics
        response_time = time.time() - start_time
        analytics = QueryAnalytics(
            query_id=query_id,
            timestamp=datetime.now(),
            question=req.question,
            model_ids=req.model_ids,
            roles=req.roles,
            method=req.method,
            consensus_score=0.0,
            response_time=response_time,
            success=False,
            error_message=str(e)
        )
        background_tasks.add_task(analytics_manager.record_query, analytics)
        
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/llm/batch")
@limiter.limit("10/minute")
async def batch_qa(
    request: Request,
    batch_req: BatchQARequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None)
):
    """Batch processing for multiple queries"""
    verify_bearer(authorization)
    
    if len(batch_req.requests) > settings.max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum of {settings.max_batch_size}"
        )
    
    batch_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        if batch_req.parallel:
            # Process requests in parallel
            tasks = []
            for qa_req in batch_req.requests:
                task = multi_llm_qa(request, qa_req, background_tasks, authorization)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Process requests sequentially
            results = []
            for qa_req in batch_req.requests:
                try:
                    result = await multi_llm_qa(request, qa_req, background_tasks, authorization)
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})
        
        response_time = time.time() - start_time
        
        return {
            "batch_id": batch_id,
            "total_requests": len(batch_req.requests),
            "successful_requests": len([r for r in results if not isinstance(r, Exception) and "error" not in r]),
            "response_time": response_time,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/analytics/summary")
async def get_analytics_summary(authorization: str = Header(None)):
    """Get analytics summary"""
    verify_bearer(authorization)
    return analytics_manager.get_summary_stats()

@app.get("/analytics/models")
async def get_model_analytics(authorization: str = Header(None)):
    """Get model performance analytics"""
    verify_bearer(authorization)
    performances = analytics_manager.get_model_performance()
    return {"model_performances": [perf.__dict__ for perf in performances]}

@app.get("/analytics/trends")
async def get_consensus_trends(days: int = 7, authorization: str = Header(None)):
    """Get consensus trends over time"""
    verify_bearer(authorization)
    return analytics_manager.get_consensus_trends(days)

@app.delete("/cache")
async def clear_cache(pattern: Optional[str] = None, authorization: str = Header(None)):
    """Clear cache entries"""
    verify_bearer(authorization)
    success = cache_manager.clear_cache(pattern)
    return {"success": success, "message": f"Cache cleared{' with pattern: ' + pattern if pattern else ''}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 