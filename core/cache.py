"""
Advanced Caching System for Mini-ERP
Provides LRU caching with time-based invalidation for improved performance
"""

from typing import Any, Optional, Dict, Callable
from functools import wraps
from datetime import datetime, timedelta
import threading
from collections import OrderedDict
from core.logger import get_logger

logger = get_logger('cache')


class LRUCache:
    """
    Thread-safe LRU (Least Recently Used) cache with TTL support
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize LRU cache
        
        Args:
            max_size: Maximum number of items to cache
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, datetime] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            # Check if key exists
            if key not in self._cache:
                self._misses += 1
                return None
            
            # Check if expired
            if self._is_expired(key):
                self._remove(key)
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        with self._lock:
            # Remove if exists
            if key in self._cache:
                self._remove(key)
            
            # Add new item
            self._cache[key] = value
            self._timestamps[key] = datetime.now()
            
            # Move to end
            self._cache.move_to_end(key)
            
            # Evict oldest if over capacity
            if len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                self._remove(oldest_key)
    
    def invalidate(self, key: str):
        """Remove specific key from cache"""
        with self._lock:
            self._remove(key)
    
    def invalidate_pattern(self, pattern: str):
        """Remove all keys matching pattern"""
        with self._lock:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                self._remove(key)
    
    def clear(self):
        """Clear entire cache"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self._timestamps:
            return True
        
        age = datetime.now() - self._timestamps[key]
        return age > timedelta(seconds=self.default_ttl)
    
    def _remove(self, key: str):
        """Remove key from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]


# Global cache instances
_product_cache = LRUCache(max_size=500, default_ttl=600)  # 10 minutes
_customer_cache = LRUCache(max_size=500, default_ttl=600)
_supplier_cache = LRUCache(max_size=200, default_ttl=600)
_query_cache = LRUCache(max_size=1000, default_ttl=300)  # 5 minutes


def cached(cache_instance: LRUCache, key_prefix: str = '', ttl: Optional[int] = None):
    """
    Decorator for caching function results
    
    Usage:
        @cached(_product_cache, 'product')
        def get_product(product_id):
            return db.fetch_one(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = cache_instance.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_instance.set(cache_key, result, ttl)
            logger.debug(f"Cache miss: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(entity_type: str, entity_id: Optional[str] = None):
    """
    Invalidate cache for specific entity or entity type
    
    Args:
        entity_type: Type of entity (product, customer, supplier)
        entity_id: Specific entity ID, or None to invalidate all of that type
    """
    cache_map = {
        'product': _product_cache,
        'customer': _customer_cache,
        'supplier': _supplier_cache,
        'query': _query_cache
    }
    
    cache = cache_map.get(entity_type)
    if not cache:
        return
    
    if entity_id:
        cache.invalidate_pattern(entity_id)
    else:
        cache.clear()
    
    logger.info(f"Cache invalidated: {entity_type} {entity_id or 'all'}")


def get_cache_stats() -> Dict[str, Dict]:
    """Get statistics for all caches"""
    return {
        'product_cache': _product_cache.get_stats(),
        'customer_cache': _customer_cache.get_stats(),
        'supplier_cache': _supplier_cache.get_stats(),
        'query_cache': _query_cache.get_stats()
    }


def clear_all_caches():
    """Clear all caches"""
    _product_cache.clear()
    _customer_cache.clear()
    _supplier_cache.clear()
    _query_cache.clear()
    logger.info("All caches cleared")


# Convenience functions for common operations
def cache_product(product_id: str, product_data: Dict):
    """Cache product data"""
    _product_cache.set(f"product:{product_id}", product_data)


def get_cached_product(product_id: str) -> Optional[Dict]:
    """Get cached product data"""
    return _product_cache.get(f"product:{product_id}")


def cache_customer(customer_id: str, customer_data: Dict):
    """Cache customer data"""
    _customer_cache.set(f"customer:{customer_id}", customer_data)


def get_cached_customer(customer_id: str) -> Optional[Dict]:
    """Get cached customer data"""
    return _customer_cache.get(f"customer:{customer_id}")
