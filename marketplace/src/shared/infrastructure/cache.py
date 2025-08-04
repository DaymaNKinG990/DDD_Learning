"""Redis cache implementation."""

# Python imports
import json
import pickle
from typing import Any, AsyncGenerator, Optional, Union
from datetime import timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from pydantic import BaseModel

# Local imports
from src.shared.infrastructure.config import settings


class CacheService:
    """
    Redis cache service.
    
    Attributes:
        redis_client: The Redis client.
        _pickle_client: The Redis client for pickle serialization.
    """
    
    def __init__(self) -> None:
        """Initialize the cache service."""
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is not available. Please install redis package.")
            
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
        """
        Get value from cache.

        Args:
            key: The key to get the value from.

        Returns:
            Optional[str]: The value from the cache.
        """
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
        """
        Set value in cache.

        Args:
            key: The key to set the value for.
            value: The value to set.
            expire: The expiration time for the key.

        Returns:
            bool: True if the value was set, False otherwise.
        """
        try:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return await self.redis_client.set(key, value, ex=expire)
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: The key to delete.

        Returns:
            bool: True if the key was deleted, False otherwise.
        """
        try:
            return bool(await self.redis_client.delete(key))
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        try:
            return bool(await self.redis_client.exists(key))
        except Exception:
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration for key.

        Args:
            key: The key to set the expiration for.
            seconds: The number of seconds to set the expiration for.

        Returns:
            bool: True if the expiration was set, False otherwise.
        """
        try:
            return bool(await self.redis_client.expire(key, seconds))
        except Exception:
            return False
    
    async def ttl(self, key: str) -> int:
        """
        Get time to live for key.

        Args:
            key: The key to get the time to live for.

        Returns:
            int: The time to live for the key.
        """
        try:
            return await self.redis_client.ttl(key)
        except Exception:
            return -1
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment key value.

        Args:
            key: The key to increment.
            amount: The amount to increment the key by.

        Returns:
            int: The new value of the key.
        """
        try:
            return await self.redis_client.incr(key, amount)
        except Exception:
            return 0
    
    # JSON serialization methods
    async def get_json(self, key: str) -> Optional[dict]:
        """
        Get JSON value from cache.

        Args:
            key: The key to get the JSON value from.

        Returns:
            Optional[dict]: The JSON value from the cache.
        """
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
        """
        Set JSON value in cache.

        Args:
            key: The key to set the JSON value for.
            value: The value to set.
            expire: The expiration time for the key.

        Returns:
            bool: True if the JSON value was set, False otherwise.
        """
        if isinstance(value, BaseModel):
            value = value.model_dump()
        return await self.set(key, json.dumps(value), expire)
    
    # Pickle serialization methods for complex objects
    async def get_pickle(self, key: str) -> Optional[Any]:
        """
        Get pickled value from cache.

        Args:
            key: The key to get the pickled value from.

        Returns:
            Optional[Any]: The pickled value from the cache.
        """
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
        """
        Set pickled value in cache.

        Args:
            key: The key to set the pickled value for.
            value: The value to set.
            expire: The expiration time for the key.

        Returns:
            bool: True if the pickled value was set, False otherwise.
        """
        try:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return await self._pickle_client.set(key, pickle.dumps(value), ex=expire)
        except Exception:
            return False
    
    # Hash operations
    async def hget(self, name: str, key: str) -> Optional[str]:
        """
        Get hash field value.

        Args:
            name: The name of the hash.
            key: The key to get the hash field value for.

        Returns:
            Optional[str]: The hash field value.
        """
        try:
            return await self.redis_client.hget(name, key)
        except Exception:
            return None
    
    async def hset(self, name: str, key: str, value: str) -> bool:
        """
        Set hash field value.

        Args:
            name: The name of the hash.
            key: The key to set the hash field value for.
            value: The value to set.

        Returns:
            bool: True if the hash field value was set, False otherwise.
        """
        try:
            return bool(await self.redis_client.hset(name, key, value))
        except Exception:
            return False
    
    async def hgetall(self, name: str) -> dict[str, str]:
        """
        Get all hash fields.

        Args:
            name: The name of the hash.

        Returns:
            dict[str, str]: The hash fields.
        """
        try:
            return await self.redis_client.hgetall(name)
        except Exception:
            return {}
    
    async def hdel(self, name: str, *keys: str) -> int:
        """
        Delete hash fields.

        Args:
            name: The name of the hash.
            keys: The keys to delete.

        Returns:
            int: The number of keys deleted.
        """
        try:
            return await self.redis_client.hdel(name, *keys)
        except Exception:
            return 0
    
    # List operations
    async def lpush(self, name: str, *values: str) -> int:
        """
        Push values to list left.

        Args:
            name: The name of the list.
            values: The values to push.

        Returns:
            int: The number of values pushed.
        """
        try:
            return await self.redis_client.lpush(name, *values)
        except Exception:
            return 0
    
    async def rpush(self, name: str, *values: str) -> int:
        """
        Push values to list right.

        Args:
            name: The name of the list.
            values: The values to push.

        Returns:
            int: The number of values pushed.
        """
        try:
            return await self.redis_client.rpush(name, *values)
        except Exception:
            return 0
    
    async def lpop(self, name: str) -> Optional[str]:
        """
        Pop value from list left.

        Args:
            name: The name of the list.

        Returns:
            Optional[str]: The value popped from the list.
        """
        try:
            return await self.redis_client.lpop(name)
        except Exception:
            return None
    
    async def rpop(self, name: str) -> Optional[str]:
        """
        Pop value from list right.

        Args:
            name: The name of the list.

        Returns:
            Optional[str]: The value popped from the list.
        """
        try:
            return await self.redis_client.rpop(name)
        except Exception:
            return None
    
    async def lrange(self, name: str, start: int, end: int) -> list:
        """
        Get list range.

        Args:
            name: The name of the list.
            start: The start index.
            end: The end index.

        Returns:
            list: The list range.
        """
        try:
            return await self.redis_client.lrange(name, start, end)
        except Exception:
            return []
    
    # Set operations
    async def sadd(self, name: str, *values: str) -> int:
        """
        Add values to set.

        Args:
            name: The name of the set.
            values: The values to add.

        Returns:
            int: The number of values added.
        """
        try:
            return await self.redis_client.sadd(name, *values)
        except Exception:
            return 0
    
    async def srem(self, name: str, *values: str) -> int:
        """
        Remove values from set.

        Args:
            name: The name of the set.
            values: The values to remove.

        Returns:
            int: The number of values removed.
        """
        try:
            return await self.redis_client.srem(name, *values)
        except Exception:
            return 0
    
    async def smembers(self, name: str) -> set:
        """
        Get all set members.

        Args:
            name: The name of the set.

        Returns:
            set: The set members.
        """
        try:
            return await self.redis_client.smembers(name)
        except Exception:
            return set()
    
    async def sismember(self, name: str, value: str) -> bool:
        """
        Check if value is in set.

        Args:
            name: The name of the set.
            value: The value to check.

        Returns:
            bool: True if the value is in the set, False otherwise.
        """
        try:
            return bool(await self.redis_client.sismember(name, value))
        except Exception:
            return False
    
    # Pattern operations
    async def keys(self, pattern: str) -> list:
        """
        Get keys matching pattern.

        Args:
            pattern: The pattern to match.

        Returns:
            list: The keys matching the pattern.
        """
        try:
            return await self.redis_client.keys(pattern)
        except Exception:
            return []
    
    async def scan_iter(self, match: Optional[str] = None, count: Optional[int] = None) -> AsyncGenerator[str, None]:
        """
        Scan keys iterator.

        Args:
            match: The pattern to match.
            count: The count of keys to return.

        Returns:
            AsyncGenerator[str]: The keys matching the pattern.
        """
        try:
            async for key in self.redis_client.scan_iter(match=match, count=count):
                yield key
        except Exception:
            return
    
    # Utility methods
    async def flushdb(self) -> bool:
        """
        Clear all keys from current database.

        Returns:
            bool: True if the keys were cleared, False otherwise.
        """
        try:
            await self.redis_client.flushdb()
            return True
        except Exception:
            return False
    
    async def ping(self) -> bool:
        """
        Test connection.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            return await self.redis_client.ping()
        except Exception:
            return False
    
    async def close(self):
        """Close connections."""
        await self.redis_client.close()
        await self._pickle_client.close()


# Global cache instance
if REDIS_AVAILABLE:
    cache = CacheService()
else:
    cache = None


class CacheManager:
    """
    Cache manager for managing multiple cache instances.
    
    Attributes:
        _instances: Dictionary of cache instances.
    """
    
    def __init__(self) -> None:
        """Initialize the cache manager."""
        self._instances: dict[str, CacheService] = {}
    
    def get_instance(self, name: str = "default") -> CacheService:
        """
        Get or create a cache instance.
        
        Args:
            name: The name of the cache instance.
            
        Returns:
            CacheService: The cache instance.
        """
        if name not in self._instances:
            self._instances[name] = CacheService()
        return self._instances[name]
    
    def remove_instance(self, name: str) -> None:
        """
        Remove a cache instance.
        
        Args:
            name: The name of the cache instance to remove.
        """
        if name in self._instances:
            del self._instances[name]
    
    async def remove_instance_async(self, name: str) -> None:
        """
        Remove a cache instance asynchronously.
        
        Args:
            name: The name of the cache instance to remove.
        """
        if name in self._instances:
            await self._instances[name].close()
            del self._instances[name]
    
    async def close_all(self) -> None:
        """Close all cache instances."""
        for instance in self._instances.values():
            await instance.close()
        self._instances.clear()


# Global cache manager instance
cache_manager = CacheManager() 