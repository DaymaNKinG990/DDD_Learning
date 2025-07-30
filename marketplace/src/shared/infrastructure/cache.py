"""Redis cache implementation."""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta

import redis.asyncio as redis
from pydantic import BaseModel

from src.shared.infrastructure.config import settings


class CacheService:
    """Redis cache service."""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.redis.url,
            encoding="utf-8",
            decode_responses=True
        )
        self._pickle_client = redis.from_url(
            settings.redis.url,
            encoding=None,
            decode_responses=False
        )
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            return await self.redis_client.get(key)
        except Exception:
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache."""
        try:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return await self.redis_client.set(key, value, ex=expire)
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(await self.redis_client.delete(key))
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return bool(await self.redis_client.exists(key))
        except Exception:
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        try:
            return bool(await self.redis_client.expire(key, seconds))
        except Exception:
            return False
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            return await self.redis_client.ttl(key)
        except Exception:
            return -1
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment key value."""
        try:
            return await self.redis_client.incr(key, amount)
        except Exception:
            return 0
    
    # JSON serialization methods
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(
        self, 
        key: str, 
        value: Union[dict, BaseModel], 
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set JSON value in cache."""
        if isinstance(value, BaseModel):
            value = value.model_dump()
        return await self.set(key, json.dumps(value), expire)
    
    # Pickle serialization methods for complex objects
    async def get_pickle(self, key: str) -> Optional[Any]:
        """Get pickled value from cache."""
        try:
            value = await self._pickle_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception:
            return None
    
    async def set_pickle(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set pickled value in cache."""
        try:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return await self._pickle_client.set(key, pickle.dumps(value), ex=expire)
        except Exception:
            return False
    
    # Hash operations
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value."""
        try:
            return await self.redis_client.hget(name, key)
        except Exception:
            return None
    
    async def hset(self, name: str, key: str, value: str) -> bool:
        """Set hash field value."""
        try:
            return bool(await self.redis_client.hset(name, key, value))
        except Exception:
            return False
    
    async def hgetall(self, name: str) -> dict:
        """Get all hash fields."""
        try:
            return await self.redis_client.hgetall(name)
        except Exception:
            return {}
    
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields."""
        try:
            return await self.redis_client.hdel(name, *keys)
        except Exception:
            return 0
    
    # List operations
    async def lpush(self, name: str, *values: str) -> int:
        """Push values to list left."""
        try:
            return await self.redis_client.lpush(name, *values)
        except Exception:
            return 0
    
    async def rpush(self, name: str, *values: str) -> int:
        """Push values to list right."""
        try:
            return await self.redis_client.rpush(name, *values)
        except Exception:
            return 0
    
    async def lpop(self, name: str) -> Optional[str]:
        """Pop value from list left."""
        try:
            return await self.redis_client.lpop(name)
        except Exception:
            return None
    
    async def rpop(self, name: str) -> Optional[str]:
        """Pop value from list right."""
        try:
            return await self.redis_client.rpop(name)
        except Exception:
            return None
    
    async def lrange(self, name: str, start: int, end: int) -> list:
        """Get list range."""
        try:
            return await self.redis_client.lrange(name, start, end)
        except Exception:
            return []
    
    # Set operations
    async def sadd(self, name: str, *values: str) -> int:
        """Add values to set."""
        try:
            return await self.redis_client.sadd(name, *values)
        except Exception:
            return 0
    
    async def srem(self, name: str, *values: str) -> int:
        """Remove values from set."""
        try:
            return await self.redis_client.srem(name, *values)
        except Exception:
            return 0
    
    async def smembers(self, name: str) -> set:
        """Get all set members."""
        try:
            return await self.redis_client.smembers(name)
        except Exception:
            return set()
    
    async def sismember(self, name: str, value: str) -> bool:
        """Check if value is in set."""
        try:
            return bool(await self.redis_client.sismember(name, value))
        except Exception:
            return False
    
    # Pattern operations
    async def keys(self, pattern: str) -> list:
        """Get keys matching pattern."""
        try:
            return await self.redis_client.keys(pattern)
        except Exception:
            return []
    
    async def scan_iter(self, match: Optional[str] = None, count: Optional[int] = None):
        """Scan keys iterator."""
        try:
            async for key in self.redis_client.scan_iter(match=match, count=count):
                yield key
        except Exception:
            return
    
    # Utility methods
    async def flushdb(self) -> bool:
        """Clear all keys from current database."""
        try:
            await self.redis_client.flushdb()
            return True
        except Exception:
            return False
    
    async def ping(self) -> bool:
        """Test connection."""
        try:
            return await self.redis_client.ping()
        except Exception:
            return False
    
    async def close(self):
        """Close connections."""
        await self.redis_client.close()
        await self._pickle_client.close()


# Global cache instance
cache = CacheService() 