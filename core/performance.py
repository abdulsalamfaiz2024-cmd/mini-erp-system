"""
Performance Monitoring for Mini-ERP System
Tracks query performance, memory usage, and system health
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque
from core.logger import get_logger

logger = get_logger('performance')


class PerformanceMonitor:
    """Monitor system performance and track metrics"""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            max_history: Maximum number of query records to keep
        """
        self.max_history = max_history
        self._query_history = deque(maxlen=max_history)
        self._lock = threading.RLock()
        self._start_time = datetime.now()
        
    def record_query(self, query: str, duration: float, rows_affected: int = 0):
        """
        Record a database query execution
        
        Args:
            query: SQL query executed
            duration: Execution time in seconds
            rows_affected: Number of rows affected
        """
        with self._lock:
            record = {
                'timestamp': datetime.now(),
                'query': query[:200],  # Truncate long queries
                'duration': duration,
                'rows_affected': rows_affected
            }
            self._query_history.append(record)
    
    def get_slow_queries(self, threshold: float = 0.1) -> List[Dict]:
        """
        Get queries slower than threshold
        
        Args:
            threshold: Minimum duration in seconds
            
        Returns:
            List of slow query records
        """
        with self._lock:
            return [q for q in self._query_history if q['duration'] > threshold]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        with self._lock:
            if not self._query_history:
                return {
                    'total_queries': 0,
                    'avg_duration': 0,
                    'min_duration': 0,
                    'max_duration': 0,
                    'slow_queries': 0
                }
            
            durations = [q['duration'] for q in self._query_history]
            
            return {
                'total_queries': len(self._query_history),
                'avg_duration': round(sum(durations) / len(durations), 4),
                'min_duration': round(min(durations), 4),
                'max_duration': round(max(durations), 4),
                'slow_queries': len([d for d in durations if d > 0.1]),
                'recent_queries': list(self._query_history)[-10:]
            }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': round(memory_info.rss / (1024 * 1024), 2),
                'vms_mb': round(memory_info.vms / (1024 * 1024), 2),
                'percent': round(process.memory_percent(), 2)
            }
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return {}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            uptime = datetime.now() - self._start_time
            
            return {
                'uptime_seconds': int(uptime.total_seconds()),
                'uptime_formatted': str(uptime).split('.')[0],
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': round(memory.available / (1024 * 1024), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024 * 1024 * 1024), 2),
                'status': 'healthy' if cpu_percent < 80 and memory.percent < 80 else 'warning'
            }
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {'status': 'unknown'}
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get all metrics for dashboard display"""
        return {
            'query_stats': self.get_query_stats(),
            'memory_usage': self.get_memory_usage(),
            'system_health': self.get_system_health()
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        with self._lock:
            self._query_history.clear()
            self._start_time = datetime.now()
            logger.info("Performance stats reset")


# Global performance monitor instance
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _monitor


def track_query(func):
    """
    Decorator to track query performance
    
    Usage:
        @track_query
        def execute_query(query, params):
            ...
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Try to extract query from args
        query = args[0] if args else 'unknown'
        _monitor.record_query(str(query), duration)
        
        return result
    
    return wrapper


class QueryTimer:
    """Context manager for timing queries"""
    
    def __init__(self, query_name: str):
        self.query_name = query_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        _monitor.record_query(self.query_name, duration)
        
        if duration > 0.1:
            logger.warning(f"Slow query detected: {self.query_name} took {duration:.3f}s")
