"""Tests for shared infrastructure cache."""

# Python imports
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import timedelta
from typing import Any

# Local imports
from src.shared.infrastructure.cache import CacheService
from pydantic import BaseModel


class MockData(BaseModel):
    """Mock data model."""
    name: str
    value: int


class TestCacheService:
    """Test cases for CacheService."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        with patch('src.shared.infrastructure.cache.redis') as mock_redis:
            mock_redis.from_url.return_value = AsyncMock()
            yield mock_redis

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        with patch('src.shared.infrastructure.cache.settings') as mock_settings:
            mock_settings.redis.url = "redis://localhost:6379"
            yield mock_settings

    @pytest.fixture
    def cache_service(self, mock_redis, mock_settings):
        """Create cache service with mocked dependencies."""
        with patch('src.shared.infrastructure.cache.REDIS_AVAILABLE', True):
            service = CacheService()
            service.redis_client = AsyncMock()
            service._pickle_client = AsyncMock()
            return service

    def test_initialization_success(self, mock_redis, mock_settings):
        """Test successful cache service initialization."""
        with patch('src.shared.infrastructure.cache.REDIS_AVAILABLE', True):
            service = CacheService()
            assert service.redis_client is not None
            assert service._pickle_client is not None

    def test_initialization_redis_not_available(self):
        """Test initialization when Redis is not available."""
        with patch('src.shared.infrastructure.cache.REDIS_AVAILABLE', False):
            with pytest.raises(ImportError, match="Redis is not available"):
                CacheService()

    @pytest.mark.asyncio
    async def test_get_success(self, cache_service):
        """Test successful get operation."""
        cache_service.redis_client.get.return_value = "test_value"
        
        result = await cache_service.get("test_key")
        
        assert result == "test_value"
        cache_service.redis_client.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_exception(self, cache_service):
        """Test get operation with exception."""
        cache_service.redis_client.get.side_effect = Exception("Redis error")
        
        result = await cache_service.get("test_key")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_set_success(self, cache_service):
        """Test successful set operation."""
        cache_service.redis_client.set.return_value = True
        
        result = await cache_service.set("test_key", "test_value")
        
        assert result is True
        cache_service.redis_client.set.assert_called_once_with("test_key", "test_value", ex=None)

    @pytest.mark.asyncio
    async def test_set_with_expire_seconds(self, cache_service):
        """Test set operation with expiration in seconds."""
        cache_service.redis_client.set.return_value = True
        
        result = await cache_service.set("test_key", "test_value", expire=300)
        
        assert result is True
        cache_service.redis_client.set.assert_called_once_with("test_key", "test_value", ex=300)

    @pytest.mark.asyncio
    async def test_set_with_expire_timedelta(self, cache_service):
        """Test set operation with expiration as timedelta."""
        cache_service.redis_client.set.return_value = True
        
        result = await cache_service.set("test_key", "test_value", expire=timedelta(minutes=5))
        
        assert result is True
        cache_service.redis_client.set.assert_called_once_with("test_key", "test_value", ex=300)

    @pytest.mark.asyncio
    async def test_set_exception(self, cache_service):
        """Test set operation with exception."""
        cache_service.redis_client.set.side_effect = Exception("Redis error")
        
        result = await cache_service.set("test_key", "test_value")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self, cache_service):
        """Test successful delete operation."""
        cache_service.redis_client.delete.return_value = 1
        
        result = await cache_service.delete("test_key")
        
        assert result is True
        cache_service.redis_client.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_not_found(self, cache_service):
        """Test delete operation for non-existent key."""
        cache_service.redis_client.delete.return_value = 0
        
        result = await cache_service.delete("test_key")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_exception(self, cache_service):
        """Test delete operation with exception."""
        cache_service.redis_client.delete.side_effect = Exception("Redis error")
        
        result = await cache_service.delete("test_key")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_expire_success(self, cache_service):
        """Test successful expire operation."""
        cache_service.redis_client.expire.return_value = True
        
        result = await cache_service.expire("test_key", 300)
        
        assert result is True
        cache_service.redis_client.expire.assert_called_once_with("test_key", 300)

    @pytest.mark.asyncio
    async def test_expire_exception(self, cache_service):
        """Test expire operation with exception."""
        cache_service.redis_client.expire.side_effect = Exception("Redis error")
        
        result = await cache_service.expire("test_key", 300)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_ttl_success(self, cache_service):
        """Test successful TTL operation."""
        cache_service.redis_client.ttl.return_value = 250
        
        result = await cache_service.ttl("test_key")
        
        assert result == 250
        cache_service.redis_client.ttl.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_ttl_exception(self, cache_service):
        """Test TTL operation with exception."""
        cache_service.redis_client.ttl.side_effect = Exception("Redis error")
        
        result = await cache_service.ttl("test_key")
        
        assert result == -1

    @pytest.mark.asyncio
    async def test_incr_success(self, cache_service):
        """Test successful increment operation."""
        cache_service.redis_client.incr.return_value = 5
        
        result = await cache_service.incr("test_key", 2)
        
        assert result == 5
        cache_service.redis_client.incr.assert_called_once_with("test_key", 2)

    @pytest.mark.asyncio
    async def test_incr_default_amount(self, cache_service):
        """Test increment operation with default amount."""
        cache_service.redis_client.incr.return_value = 3
        
        result = await cache_service.incr("test_key")
        
        assert result == 3
        cache_service.redis_client.incr.assert_called_once_with("test_key", 1)

    @pytest.mark.asyncio
    async def test_incr_exception(self, cache_service):
        """Test increment operation with exception."""
        cache_service.redis_client.incr.side_effect = Exception("Redis error")
        
        result = await cache_service.incr("test_key")
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_get_json_success(self, cache_service):
        """Test successful JSON get operation."""
        cache_service.redis_client.get.return_value = '{"name": "test", "value": 123}'
        
        result = await cache_service.get_json("test_key")
        
        assert result == {"name": "test", "value": 123}

    @pytest.mark.asyncio
    async def test_get_json_none(self, cache_service):
        """Test JSON get operation for non-existent key."""
        cache_service.redis_client.get.return_value = None
        
        result = await cache_service.get_json("test_key")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_json_invalid_json(self, cache_service):
        """Test JSON get operation with invalid JSON."""
        cache_service.redis_client.get.return_value = "invalid json"
        
        result = await cache_service.get_json("test_key")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_set_json_dict_success(self, cache_service):
        """Test successful JSON set operation with dict."""
        cache_service.redis_client.set.return_value = True
        
        result = await cache_service.set_json("test_key", {"name": "test", "value": 123})
        
        assert result is True
        cache_service.redis_client.set.assert_called_once_with("test_key", '{"name": "test", "value": 123}', ex=None)

    @pytest.mark.asyncio
    async def test_set_json_pydantic_success(self, cache_service):
        """Test successful JSON set operation with Pydantic model."""
        cache_service.redis_client.set.return_value = True
        test_data = MockData(name="test", value=123)
        
        result = await cache_service.set_json("test_key", test_data)
        
        assert result is True
        cache_service.redis_client.set.assert_called_once_with("test_key", '{"name": "test", "value": 123}', ex=None)

    @pytest.mark.asyncio
    async def test_set_json_exception(self, cache_service):
        """Test JSON set operation with exception."""
        cache_service.redis_client.set.side_effect = Exception("Redis error")
        
        result = await cache_service.set_json("test_key", {"test": "data"})
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_pickle_success(self, cache_service):
        """Test successful pickle get operation."""
        test_data = {"name": "test", "value": 123}
        with patch('pickle.loads', return_value=test_data):
            cache_service._pickle_client.get.return_value = b"pickled_data"
            
            result = await cache_service.get_pickle("test_key")
            
            assert result == test_data

    @pytest.mark.asyncio
    async def test_get_pickle_none(self, cache_service):
        """Test pickle get operation for non-existent key."""
        cache_service._pickle_client.get.return_value = None
        
        result = await cache_service.get_pickle("test_key")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_pickle_exception(self, cache_service):
        """Test pickle get operation with exception."""
        cache_service._pickle_client.get.side_effect = Exception("Redis error")
        
        result = await cache_service.get_pickle("test_key")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_set_pickle_success(self, cache_service):
        """Test successful pickle set operation."""
        cache_service._pickle_client.set.return_value = True
        test_data = {"name": "test", "value": 123}
        
        with patch('pickle.dumps', return_value=b"pickled_data"):
            result = await cache_service.set_pickle("test_key", test_data)
            
            assert result is True
            cache_service._pickle_client.set.assert_called_once_with("test_key", b"pickled_data", ex=None)

    @pytest.mark.asyncio
    async def test_set_pickle_exception(self, cache_service):
        """Test pickle set operation with exception."""
        cache_service._pickle_client.set.side_effect = Exception("Redis error")
        
        result = await cache_service.set_pickle("test_key", {"test": "data"})
        
        assert result is False

    @pytest.mark.asyncio
    async def test_hget_success(self, cache_service):
        """Test successful hash get operation."""
        cache_service.redis_client.hget.return_value = "test_value"
        
        result = await cache_service.hget("test_hash", "test_key")
        
        assert result == "test_value"
        cache_service.redis_client.hget.assert_called_once_with("test_hash", "test_key")

    @pytest.mark.asyncio
    async def test_hget_exception(self, cache_service):
        """Test hash get operation with exception."""
        cache_service.redis_client.hget.side_effect = Exception("Redis error")
        
        result = await cache_service.hget("test_hash", "test_key")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_hset_success(self, cache_service):
        """Test successful hash set operation."""
        cache_service.redis_client.hset.return_value = 1
        
        result = await cache_service.hset("test_hash", "test_key", "test_value")
        
        assert result is True
        cache_service.redis_client.hset.assert_called_once_with("test_hash", "test_key", "test_value")

    @pytest.mark.asyncio
    async def test_hset_exception(self, cache_service):
        """Test hash set operation with exception."""
        cache_service.redis_client.hset.side_effect = Exception("Redis error")
        
        result = await cache_service.hset("test_hash", "test_key", "test_value")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_hgetall_success(self, cache_service):
        """Test successful hash get all operation."""
        cache_service.redis_client.hgetall.return_value = {"key1": "value1", "key2": "value2"}
        
        result = await cache_service.hgetall("test_hash")
        
        assert result == {"key1": "value1", "key2": "value2"}
        cache_service.redis_client.hgetall.assert_called_once_with("test_hash")

    @pytest.mark.asyncio
    async def test_hgetall_exception(self, cache_service):
        """Test hash get all operation with exception."""
        cache_service.redis_client.hgetall.side_effect = Exception("Redis error")
        
        result = await cache_service.hgetall("test_hash")
        
        assert result == {}

    @pytest.mark.asyncio
    async def test_hdel_success(self, cache_service):
        """Test successful hash delete operation."""
        cache_service.redis_client.hdel.return_value = 2
        
        result = await cache_service.hdel("test_hash", "key1", "key2")
        
        assert result == 2
        cache_service.redis_client.hdel.assert_called_once_with("test_hash", "key1", "key2")

    @pytest.mark.asyncio
    async def test_hdel_exception(self, cache_service):
        """Test hash delete operation with exception."""
        cache_service.redis_client.hdel.side_effect = Exception("Redis error")
        
        result = await cache_service.hdel("test_hash", "key1")
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_lpush_success(self, cache_service):
        """Test successful list push operation."""
        cache_service.redis_client.lpush.return_value = 3
        
        result = await cache_service.lpush("test_list", "value1", "value2", "value3")
        
        assert result == 3
        cache_service.redis_client.lpush.assert_called_once_with("test_list", "value1", "value2", "value3")

    @pytest.mark.asyncio
    async def test_lpush_exception(self, cache_service):
        """Test list push operation with exception."""
        cache_service.redis_client.lpush.side_effect = Exception("Redis error")
        
        result = await cache_service.lpush("test_list", "value1")
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_rpush_success(self, cache_service):
        """Test successful list right push operation."""
        cache_service.redis_client.rpush.return_value = 3
        
        result = await cache_service.rpush("test_list", "value1", "value2", "value3")
        
        assert result == 3
        cache_service.redis_client.rpush.assert_called_once_with("test_list", "value1", "value2", "value3")

    @pytest.mark.asyncio
    async def test_rpush_exception(self, cache_service):
        """Test list right push operation with exception."""
        cache_service.redis_client.rpush.side_effect = Exception("Redis error")
        
        result = await cache_service.rpush("test_list", "value1")
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_lpop_success(self, cache_service):
        """Test successful list pop operation."""
        cache_service.redis_client.lpop.return_value = "value1"
        
        result = await cache_service.lpop("test_list")
        
        assert result == "value1"
        cache_service.redis_client.lpop.assert_called_once_with("test_list")

    @pytest.mark.asyncio
    async def test_lpop_exception(self, cache_service):
        """Test list pop operation with exception."""
        cache_service.redis_client.lpop.side_effect = Exception("Redis error")
        
        result = await cache_service.lpop("test_list")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_rpop_success(self, cache_service):
        """Test successful list right pop operation."""
        cache_service.redis_client.rpop.return_value = "value1"
        
        result = await cache_service.rpop("test_list")
        
        assert result == "value1"
        cache_service.redis_client.rpop.assert_called_once_with("test_list")

    @pytest.mark.asyncio
    async def test_rpop_exception(self, cache_service):
        """Test list right pop operation with exception."""
        cache_service.redis_client.rpop.side_effect = Exception("Redis error")
        
        result = await cache_service.rpop("test_list")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_lrange_success(self, cache_service):
        """Test successful list range operation."""
        cache_service.redis_client.lrange.return_value = ["value1", "value2", "value3"]
        
        result = await cache_service.lrange("test_list", 0, 2)
        
        assert result == ["value1", "value2", "value3"]
        cache_service.redis_client.lrange.assert_called_once_with("test_list", 0, 2)

    @pytest.mark.asyncio
    async def test_lrange_exception(self, cache_service):
        """Test list range operation with exception."""
        cache_service.redis_client.lrange.side_effect = Exception("Redis error")
        
        result = await cache_service.lrange("test_list", 0, 2)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_sadd_success(self, cache_service):
        """Test successful set add operation."""
        cache_service.redis_client.sadd.return_value = 2
        
        result = await cache_service.sadd("test_set", "value1", "value2")
        
        assert result == 2
        cache_service.redis_client.sadd.assert_called_once_with("test_set", "value1", "value2")

    @pytest.mark.asyncio
    async def test_sadd_exception(self, cache_service):
        """Test set add operation with exception."""
        cache_service.redis_client.sadd.side_effect = Exception("Redis error")
        
        result = await cache_service.sadd("test_set", "value1")
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_srem_success(self, cache_service):
        """Test successful set remove operation."""
        cache_service.redis_client.srem.return_value = 1
        
        result = await cache_service.srem("test_set", "value1")
        
        assert result == 1
        cache_service.redis_client.srem.assert_called_once_with("test_set", "value1")

    @pytest.mark.asyncio
    async def test_srem_exception(self, cache_service):
        """Test set remove operation with exception."""
        cache_service.redis_client.srem.side_effect = Exception("Redis error")
        
        result = await cache_service.srem("test_set", "value1")
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_smembers_success(self, cache_service):
        """Test successful set members operation."""
        cache_service.redis_client.smembers.return_value = {"value1", "value2"}
        
        result = await cache_service.smembers("test_set")
        
        assert result == {"value1", "value2"}
        cache_service.redis_client.smembers.assert_called_once_with("test_set")

    @pytest.mark.asyncio
    async def test_smembers_exception(self, cache_service):
        """Test set members operation with exception."""
        cache_service.redis_client.smembers.side_effect = Exception("Redis error")
        
        result = await cache_service.smembers("test_set")
        
        assert result == set()

    @pytest.mark.asyncio
    async def test_sismember_success(self, cache_service):
        """Test successful set is member operation."""
        cache_service.redis_client.sismember.return_value = True
        
        result = await cache_service.sismember("test_set", "value1")
        
        assert result is True
        cache_service.redis_client.sismember.assert_called_once_with("test_set", "value1")

    @pytest.mark.asyncio
    async def test_sismember_exception(self, cache_service):
        """Test set is member operation with exception."""
        cache_service.redis_client.sismember.side_effect = Exception("Redis error")
        
        result = await cache_service.sismember("test_set", "value1")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_keys_success(self, cache_service):
        """Test successful keys operation."""
        cache_service.redis_client.keys.return_value = ["key1", "key2", "key3"]
        
        result = await cache_service.keys("test_*")
        
        assert result == ["key1", "key2", "key3"]
        cache_service.redis_client.keys.assert_called_once_with("test_*")

    @pytest.mark.asyncio
    async def test_keys_exception(self, cache_service):
        """Test keys operation with exception."""
        cache_service.redis_client.keys.side_effect = Exception("Redis error")
        
        result = await cache_service.keys("test_*")
        
        assert result == []

    @pytest.mark.asyncio
    async def test_scan_iter_success(self, cache_service):
        """Test successful scan iter operation."""
        # Create a proper async generator mock
        async def mock_scan_iter(match=None, count=None):
            yield "key1"
            yield "key2"
            yield "key3"
        
        cache_service.redis_client.scan_iter = mock_scan_iter
        
        result = []
        async for key in cache_service.scan_iter("test_*"):
            result.append(key)
        
        assert result == ["key1", "key2", "key3"]

    @pytest.mark.asyncio
    async def test_scan_iter_exception(self, cache_service):
        """Test scan iter operation with exception."""
        async def mock_scan_iter_exception(match=None, count=None):
            raise Exception("Redis error")
        
        # Replace the mock with our custom async generator
        cache_service.redis_client.scan_iter = mock_scan_iter_exception
        
        result = []
        # Suppress RuntimeWarning for this specific test
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            async for key in cache_service.scan_iter("test_*"):
                result.append(key)
        
        # When exception occurs, scan_iter should return empty result
        assert result == []

    @pytest.mark.asyncio
    async def test_flushdb_success(self, cache_service):
        """Test successful flush database operation."""
        cache_service.redis_client.flushdb.return_value = True
        
        result = await cache_service.flushdb()
        
        assert result is True
        cache_service.redis_client.flushdb.assert_called_once()

    @pytest.mark.asyncio
    async def test_flushdb_exception(self, cache_service):
        """Test flush database operation with exception."""
        cache_service.redis_client.flushdb.side_effect = Exception("Redis error")
        
        result = await cache_service.flushdb()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_ping_success(self, cache_service):
        """Test successful ping operation."""
        cache_service.redis_client.ping.return_value = True
        
        result = await cache_service.ping()
        
        assert result is True
        cache_service.redis_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_exception(self, cache_service):
        """Test ping operation with exception."""
        cache_service.redis_client.ping.side_effect = Exception("Redis error")
        
        result = await cache_service.ping()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_close(self, cache_service):
        """Test close operation."""
        await cache_service.close()
        
        cache_service.redis_client.close.assert_called_once()
        cache_service._pickle_client.close.assert_called_once()