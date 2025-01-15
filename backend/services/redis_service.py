import redis
import json
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
            #print(f"Setting key: {key}, value type: {type(value)}")
            serialized_value = json.dumps(value)
            expiry_seconds = int(expiry_hours * 3600)  # Convert hours to seconds
            return self.redis_client.setex(key, expiry_seconds, serialized_value)
        except Exception as e:
            print(f"Error setting Redis key {key}: {str(e)}")
            return False

    def set_without_expiry(self, key, value):
        """
        Set a key-value pair without expiration time.
        
        Args:
            key (str): Redis key
            value (any): Value to store (will be JSON serialized)
        """
        try:
            serialized_value = json.dumps(value)  # Serialize the value to JSON
            self.redis_client.set(key, serialized_value)  # Store the value without expiration
            print(f"✅ Set key '{key}' without expiration.")
        except Exception as e:
            print(f"❌ Error setting Redis key {key}: {str(e)}")

    def ssad(self, key, value):
        try:
            serialized_value = json.dumps(value) 
            self.redis_client.sadd(key, serialized_value)
        except Exception as e:
            print(f"❌ Error setting Redis key {key}: {str(e)}")
        

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

    def get_smembers(self, key):
        """
        Get value for a key.
        
        Args:
            key (str): Redis key
        
        Returns:
            The deserialized value or None if key doesn't exist
        """
        try:
            value = self.redis_client.smembers(key)
            print(f"get_raw({key}) type {type(value)}")
            return value if value else None
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
        
    def flush_keys_by_pattern(self, pattern):
        """
        Flush (delete) all keys matching a specific pattern in Redis using SCAN.
        Args:
            pattern (str): The pattern to match keys (e.g., 'character:*').
        Returns:
            int: The number of keys deleted.
        """
        try:
            cursor = 0
            num_deleted = 0
            while True:
                # Use SCAN to get keys matching the pattern
                cursor, keys_to_delete = self.redis_client.scan(cursor, match=pattern)
                if keys_to_delete:
                    # Delete each key
                    self.redis_client.delete(*keys_to_delete)
                    num_deleted += len(keys_to_delete)
                
                # If cursor is 0, we are done
                if cursor == 0:
                    break
            
            print(f"✅ Deleted {num_deleted} keys matching pattern '{pattern}'.")
            return num_deleted
        except Exception as e:
            print(f"❌ Error flushing keys by pattern '{pattern}': {str(e)}")
            return 0
        
    def get_cache_key(self, prefix, *args):
        """
        Generate a cache key from prefix and arguments.
        
        Args:
            prefix (str): Prefix for the cache key
            *args: Variable arguments to include in the key
        """
        return f"rpg:{prefix}:{':'.join(str(arg) for arg in args)}"
    
    def query_characters(self, field, value):
        """
        Query characters based on a specific field and value.
        
        Args:
            field (str): The field to query (e.g., 'name', 'deeplevel').
            value (str): The value to match against the field.
        
        Returns:
            list: A list of character IDs that match the query.
        """
        matching_characters = []
        try:
            # Get all keys that match the character pattern
            keys = self.redis_client.keys("rpg:characters:*")
            
            for key in keys:
                # Get character data and convert it to a dictionary
                character_data = self.redis_client.get(key)
                if character_data:
                    character_data = json.loads(character_data)  
                    if character_data and character_data[field] == value:
                        matching_characters.append(character_data)  
            
            print(f"✅ Found {len(matching_characters)} matching characters for {field} = {value}.")
        except Exception as e:
            print(f"❌ Error querying characters: {str(e)}")
        
        return matching_characters    
    

    def get_by_pattern(self, pattern):
        """
        Retrieve all values matching a specific pattern in Redis using SCAN.
        
        Args:
            pattern (str): The pattern to match keys (e.g., 'character:*').
        
        Returns:
            dict: A dictionary of keys and their corresponding values.
        """
        results = {}
        cursor = 0

        try:
            while True:
                # Use SCAN to get keys matching the pattern
                cursor, keys = self.redis_client.scan(cursor, match=pattern)
                if keys:
                    for key in keys:
                        # Get the value for each key
                        value = self.redis_client.get(key)
                        if value is not None:
                            # Deserialize the JSON value
                            results[key] = json.loads(value)

                # If cursor is 0, we are done
                if cursor == 0:
                    break

            print(f"✅ Retrieved {len(results)} keys matching pattern '{pattern}'.")
            return results

        except Exception as e:
            print(f"❌ Error retrieving keys by pattern '{pattern}': {str(e)}")
            return {}