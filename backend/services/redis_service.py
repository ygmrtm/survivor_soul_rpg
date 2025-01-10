import redis
import json
from redis import ConnectionPool
from config import REDIS_URL

class RedisService:
    _instance = None
    _pool = None

    def __new__(cls):
        """Implement Singleton pattern to ensure only one instance of RedisService exists."""
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Redis connection pool if it doesn't exist."""
        if RedisService._pool is None:
            try:
                # Create a connection pool using from_url
                RedisService._pool = redis.ConnectionPool.from_url(
                    REDIS_URL,
                    decode_responses=True,  # Automatically decode responses to Python strings
                    max_connections=10,     # Maximum number of connections in the pool
                    socket_timeout=5,       # Socket timeout in seconds
                    retry_on_timeout=True   # Retry on timeout
                )
                
                # Test the connection
                test_client = redis.Redis(connection_pool=RedisService._pool)
                test_client.ping()
                print("✅ Successfully connected to Redis Cloud!")
            except redis.ConnectionError as e:
                print(f"❌ Failed to connect to Redis Cloud: {str(e)}")
                raise
            except Exception as e:
                print(f"❌ Unexpected error connecting to Redis Cloud: {str(e)}")
                raise

    @property
    def redis_client(self):
        """Get a Redis client from the connection pool."""
        if not RedisService._pool:
            raise Exception("Redis connection pool not initialized")
        return redis.Redis(connection_pool=RedisService._pool)


    def get_connection_info(self):
        """Get Redis connection information (for debugging)."""
        try:
            info = self.redis_client.info()
            return {
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "total_connections_received": info.get("total_connections_received")
            }
        except Exception as e:
            print(f"Error getting Redis info: {str(e)}")
            return None

    def set_with_expiry(self, key, value, expiry_hours=24):
        """
        Set a key-value pair with expiration time.
        
        Args:
            key (str): Redis key
            value (any): Value to store (will be JSON serialized)
            expiry_hours (int): Hours until the key expires
        """
        try:
            serialized_value = json.dumps(value)
            expiry_seconds = int(expiry_hours * 3600)  # Convert hours to seconds
            return self.redis_client.setex(key, expiry_seconds, serialized_value)
        except Exception as e:
            print(f"Error setting Redis key {key}: {str(e)}")
            return False

    def get(self, key):
        """
        Get value for a key.
        
        Args:
            key (str): Redis key
        
        Returns:
            The deserialized value or None if key doesn't exist
        """
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Error getting Redis key {key}: {str(e)}")
            return None

    def delete(self, key):
        """
        Delete a key.
        
        Args:
            key (str): Redis key to delete
        """
        try:
            return self.redis_client.delete(key)
        except Exception as e:
            print(f"Error deleting Redis key {key}: {str(e)}")
            return False

    def exists(self, key):
        """
        Check if a key exists.
        
        Args:
            key (str): Redis key to check
        """
        try:
            return self.redis_client.exists(key)
        except Exception as e:
            print(f"Error checking Redis key {key}: {str(e)}")
            return False

    def flush_all(self):
        """Flush all keys in the current database."""
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            print(f"Error flushing Redis database: {str(e)}")
            return False

    def get_cache_key(self, prefix, *args):
        """
        Generate a cache key from prefix and arguments.
        
        Args:
            prefix (str): Prefix for the cache key
            *args: Variable arguments to include in the key
        """
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"