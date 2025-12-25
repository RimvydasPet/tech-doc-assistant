"""Rate limiting implementation for API requests."""
import time
from typing import Dict, Tuple
from collections import deque
from logger import logger


class RateLimiter:
    """Simple rate limiter using sliding window algorithm."""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window: Time window in seconds (default: 60 seconds)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_times: Dict[str, deque] = {}
        logger.info(f"Rate limiter initialized: {max_requests} requests per {time_window}s")
    
    def is_allowed(self, session_id: str) -> Tuple[bool, int, int]:
        """
        Check if a request is allowed for the given session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Tuple of (is_allowed, requests_made, requests_remaining)
        """
        current_time = time.time()
        
        # Initialize session if not exists
        if session_id not in self.request_times:
            self.request_times[session_id] = deque()
        
        # Get request times for this session
        times = self.request_times[session_id]
        
        # Remove requests outside the time window
        cutoff_time = current_time - self.time_window
        while times and times[0] < cutoff_time:
            times.popleft()
        
        # Check if limit exceeded
        requests_made = len(times)
        requests_remaining = max(0, self.max_requests - requests_made)
        
        if requests_made >= self.max_requests:
            logger.warning(f"Rate limit exceeded for session {session_id[:8]}...")
            return False, requests_made, 0
        
        return True, requests_made, requests_remaining
    
    def record_request(self, session_id: str) -> None:
        """
        Record a request for the given session.
        
        Args:
            session_id: Unique identifier for the session
        """
        current_time = time.time()
        
        if session_id not in self.request_times:
            self.request_times[session_id] = deque()
        
        self.request_times[session_id].append(current_time)
        logger.debug(f"Request recorded for session {session_id[:8]}...")
    
    def get_wait_time(self, session_id: str) -> int:
        """
        Get the number of seconds until the next request is allowed.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Seconds to wait (0 if request is allowed now)
        """
        if session_id not in self.request_times:
            return 0
        
        times = self.request_times[session_id]
        if len(times) < self.max_requests:
            return 0
        
        # Calculate when the oldest request will expire
        oldest_request = times[0]
        current_time = time.time()
        wait_time = int(self.time_window - (current_time - oldest_request)) + 1
        
        return max(0, wait_time)
    
    def reset_session(self, session_id: str) -> None:
        """
        Reset rate limit for a specific session.
        
        Args:
            session_id: Unique identifier for the session
        """
        if session_id in self.request_times:
            del self.request_times[session_id]
            logger.info(f"Rate limit reset for session {session_id[:8]}...")
    
    def cleanup_old_sessions(self, max_age: int = 3600) -> None:
        """
        Remove sessions that haven't made requests recently.
        
        Args:
            max_age: Maximum age in seconds for keeping session data
        """
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        sessions_to_remove = []
        for session_id, times in self.request_times.items():
            if not times or times[-1] < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.request_times[session_id]
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
