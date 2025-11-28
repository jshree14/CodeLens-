"""
Simple in-memory cache for analysis results
Can be upgraded to Redis later for production
"""

import hashlib
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AnalysisCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl  # Time to live in seconds (default 1 hour)
        logger.info(f"Analysis cache initialized with TTL: {ttl}s")
    
    def _get_cache_key(self, code: str, language: str) -> str:
        """Generate cache key from code and language"""
        content = f"{code}:{language}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, code: str, language: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        key = self._get_cache_key(code, language)
        
        if key in self.cache:
            cached_data = self.cache[key]
            
            # Check if expired
            if time.time() - cached_data['timestamp'] < self.ttl:
                logger.info(f"Cache HIT for key: {key[:8]}...")
                return cached_data['result']
            else:
                # Remove expired entry
                logger.info(f"Cache EXPIRED for key: {key[:8]}...")
                del self.cache[key]
        
        logger.info(f"Cache MISS for key: {key[:8]}...")
        return None
    
    def set(self, code: str, language: str, result: Dict[str, Any]) -> None:
        """Store result in cache"""
        key = self._get_cache_key(code, language)
        
        self.cache[key] = {
            'result': result,
            'timestamp': time.time()
        }
        
        logger.info(f"Cache SET for key: {key[:8]}... (total cached: {len(self.cache)})")
        
        # Clean up old entries if cache gets too large
        if len(self.cache) > 1000:
            self._cleanup_old_entries()
    
    def _cleanup_old_entries(self) -> None:
        """Remove expired entries to prevent memory bloat"""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.cache.items()
            if current_time - data['timestamp'] >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        logger.info(f"Cache cleanup: removed {len(expired_keys)} expired entries")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "ttl_seconds": self.ttl,
            "oldest_entry_age": min(
                (time.time() - data['timestamp'] for data in self.cache.values()),
                default=0
            )
        }


# Global cache instance
analysis_cache = AnalysisCache(ttl=3600)  # 1 hour TTL
