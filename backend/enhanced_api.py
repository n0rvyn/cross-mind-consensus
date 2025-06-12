"""Enhanced Cross-Mind Consensus API with Advanced Features"""

import asyncio
import json
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import (
    BackgroundTasks,
    FastAPI,
    Header,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

sys.path.append("..")
from analytics_manager import QueryAnalytics, analytics_manager
from cache_manager import cache_manager

from config import MODEL_CONFIG, settings

# Initialize FastAPI
app = FastAPI(
    title="Enhanced Cross-Mind Consensus API",
    description="Advanced multi-LLM consensus system",
    version="2.0.0",
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global state
websocket_connections: List[WebSocket] = []


class QARequest(BaseModel):
    question: str
    roles: List[str]
    model_ids: List[str]
    method: str = "agreement"
    chain_depth: int = 2
    weights: Optional[List[float]] = None
    save_log: bool = True
    use_cache: bool = True


@app.get("/")
async def root():
    return {
        "message": "Enhanced Cross-Mind Consensus API v2.0",
        "features": [
            "Multi-LLM consensus",
            "WebSocket updates",
            "Caching",
            "Analytics",
        ],
        "status": "active",
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_text(
                json.dumps(
                    {"type": "heartbeat", "timestamp": datetime.now().isoformat()}
                )
            )
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


@app.get("/health")
async def health_check():
    cache_stats = cache_manager.get_cache_stats()
    return {
        "status": "healthy",
        "cache": cache_stats,
        "websocket_connections": len(websocket_connections),
    }


@app.post("/llm/qa")
@limiter.limit("100/minute")
async def multi_llm_qa(
    request: Request, req: QARequest, authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")

    # Simple implementation for now
    return {
        "query_id": str(uuid.uuid4()),
        "question": req.question,
        "consensus_score": 0.85,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
