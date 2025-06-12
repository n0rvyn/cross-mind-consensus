"""
Advanced Cache Manager for Cross-Mind Consensus System
Supports Redis-based caching with fallback to in-memory caching
"""

import json
import hashlib
import pickle
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import logging
from cachetools import TTLCache
import sys
sys.path.append('..')
from config import settings

# Try to import Redis, fallback to in-memory cache if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available, using in-memory cache")

logger = logging.getLogger(__name__)

class CacheManager:
    """Advanced cache manager with Redis and in-memory fallback"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = TTLCache(maxsize=1000, ttl=settings.cache_ttl_seconds)
        self.embedding_cache = TTLCache(maxsize=10000, ttl=settings.cache_embedding_ttl_seconds)
        
        if settings.enable_caching and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    password=settings.redis_password if settings.redis_password else None,
                    db=settings.redis_db,
                    encoding='utf-8',
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using in-memory cache")
                self.redis_client = None
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate a consistent cache key from data"""
        serialized = json.dumps(data, sort_keys=True) if isinstance(data, (dict, list)) else str(data)
        hash_obj = hashlib.md5(serialized.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not settings.enable_caching:
            return None
        
        try:
            # Try Redis first
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            
            # Fallback to memory cache
            return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not settings.enable_caching:
            return False
        
        ttl = ttl or settings.cache_ttl_seconds
        
        try:
            # Try Redis first
            if self.redis_client:
                serialized = json.dumps(value)
                return self.redis_client.setex(key, ttl, serialized)
            
            # Fallback to memory cache
            self.memory_cache[key] = value
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get_llm_response(self, model_id: str, prompt: str) -> Optional[str]:
        """Get cached LLM response"""
        key = self._generate_key("llm_response", {"model": model_id, "prompt": prompt})
        return self.get(key)
    
    def set_llm_response(self, model_id: str, prompt: str, response: str) -> bool:
        """Cache LLM response"""
        key = self._generate_key("llm_response", {"model": model_id, "prompt": prompt})
        return self.set(key, response)
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding"""
        key = self._generate_key("embedding", text)
        cached = self.get(key)
        return cached if cached else None
    
    def set_embedding(self, text: str, embedding: List[float]) -> bool:
        """Cache embedding"""
        key = self._generate_key("embedding", text)
        return self.set(key, embedding, settings.cache_embedding_ttl_seconds)
    
    def get_consensus_score(self, question: str, model_ids: List[str], roles: List[str]) -> Optional[Dict]:
        """Get cached consensus score"""
        key = self._generate_key("consensus", {
            "question": question,
            "models": sorted(model_ids),
            "roles": sorted(roles)
        })
        return self.get(key)
    
    def set_consensus_score(self, question: str, model_ids: List[str], roles: List[str], result: Dict) -> bool:
        """Cache consensus score"""
        key = self._generate_key("consensus", {
            "question": question,
            "models": sorted(model_ids),
            "roles": sorted(roles)
        })
        return self.set(key, result)
    
    def clear_cache(self, pattern: Optional[str] = None) -> bool:
        """Clear cache entries"""
        try:
            if self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return self.redis_client.delete(*keys) > 0
                else:
                    return self.redis_client.flushdb()
            
            # Clear memory cache
            if pattern:
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for k in keys_to_delete:
                    del self.memory_cache[k]
            else:
                self.memory_cache.clear()
                self.embedding_cache.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "enabled": settings.enable_caching,
            "redis_available": self.redis_client is not None,
            "memory_cache_size": len(self.memory_cache),
            "embedding_cache_size": len(self.embedding_cache),
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats.update({
                    "redis_memory_used": info.get("used_memory_human", "N/A"),
                    "redis_keys": self.redis_client.dbsize(),
                    "redis_hits": info.get("keyspace_hits", 0),
                    "redis_misses": info.get("keyspace_misses", 0),
                })
            except Exception as e:
                stats["redis_error"] = str(e)
        
        return stats

# Global cache manager instance
cache_manager = CacheManager() 