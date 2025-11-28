"""
Simple rate limiter for API endpoints
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        logger.info(f"Rate limiter initialized: {requests_per_minute} requests/minute")
    
    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if request is allowed
        Returns: (is_allowed, remaining_requests)
        """
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean up old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check if limit exceeded
        request_count = len(self.requests[client_id])
        
        if request_count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False, 0
        
        # Add current request
        self.requests[client_id].append(current_time)
        remaining = self.requests_per_minute - request_count - 1
        
        return True, remaining
    
    def get_stats(self, client_id: str) -> Dict[str, int]:
        """Get rate limit stats for a client"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        recent_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        return {
            "requests_in_last_minute": len(recent_requests),
            "limit": self.requests_per_minute,
            "remaining": max(0, self.requests_per_minute - len(recent_requests))
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=30)
