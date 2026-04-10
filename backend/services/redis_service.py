import redis
import json
from config import REDIS_URL
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

class RedisService:
    _instance = None
    _pool = None
    expiry_hours = 96
    expiry_minutes = 60
    limit_redis_results = 75
    
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
            print(f"Error getting Redis key {key} | {str(e)}")
            return None

    def expire(self, key, expiry_seconds):
        try:
            print(key,expiry_seconds)
            respon = self.redis_client.expire(key, expiry_seconds, lt=True)
            return respon
        except Exception as e:
            print(f"❌ Error expiring Redis key {key} by {expiry_seconds} seconds: {str(e)}")

    def zincrby(self, board, value_increment, key):
        try:
            respon = self.redis_client.zincrby(board, float(value_increment), key)
            return respon
        except Exception as e:
            print(f"❌ Error zincrby Redis key {key}: {str(e)}")            

    def ssad(self, key, value, expiry_seconds=3600 ):
        try:
            serialized_value = json.dumps(value) 
            respon = self.redis_client.sadd(key, serialized_value)
            return respon
        except Exception as e:
            print(f"❌ Error setting Redis key {key}: {str(e)}")       

    def srem(self, key, member):
        try:
            respon = self.redis_client.srem(key, member)
            return respon
        except Exception as e:
            print(f"❌ Error removing Redis key {key} for member {member}: {str(e)}")       

    def sscan(self, name, match, count=100):
        try:
            result = self.redis_client.sscan(name=name, match=match, count=count)
            print(f"sscan({name}, {match}, {count}) ? { result }")
            return result
        except Exception as e:
            print(f"Error sscan({name}, {match}, {count}): {str(e)}")
            return None

    def smembers(self, key):
        try:
            value = self.redis_client.smembers(key)
            print(f"smembers({key}) type {type(value)}")
            return value if value else None
        except Exception as e:
            print(f"Error getting Redis key {key}: {str(e)}")
            return None

    def hset(self, name, key, value ):
        try:
            serialized_value = json.dumps(value) 
            result = self.redis_client.hset(name=name, key=key, value=serialized_value)
            return result 
        except Exception as e:
            print(f"Error setting Redis key {key}: {str(e)}")
            return None

    def hgetall(self, key, character_id):
        try:
            doc = self.redis_client.hgetall(key)
            if not doc:
                return None
            clean_data = {k: v for k, v in doc.items() if not k.startswith('_')}
            clean_data['id'] = character_id
            return self.adjust_character(clean_data)
        except Exception as e:
            print(f"Error getting Redis key {key} | {str(e)}")
            return None

    def set_character_hash(self, key, character, expiry_seconds=3600):
        try:
            expiry_seconds = round(expiry_seconds / 3) if character['status'] != 'alive' and character['deep_level'] == 'l3'  else expiry_seconds
            old_status = str(self.redis_client.hget(key,'status')).replace('"','')
            change_status = old_status != character['status']
            #print(f"moving from {old_status} to {character['status']} | {character['id']}:{character['name']} = {change_status}")
            if change_status :
                self.srem(self.get_cache_key('sets', character['deep_level'] + ':' + old_status ) , key)
                set_name = self.get_cache_key('sets', character['deep_level'] + ':' + character['status']) 
                self.ssad(set_name, key )
                self.redis_client.expire(name=set_name, time=expiry_seconds)
                #print(f"del viejo status {old_status} añadiendo al set {set_name}")
            self.hset(key, 'status' , character['status']  )
            self.hset(key, 'name' , character['name'] )
            self.hset(key, 'picture' , character['picture']  )
            self.hset(key, 'notionid' , character['notionid']  )
            self.hset(key, 'level' , int(character['level'])  )
            self.hset(key, 'coins' , float(character['coins'])  )
            self.hset(key, 'xp' , int(character['xp'])  )
            self.hset(key, 'max_xp' , int(character['max_xp'])  )
            self.hset(key, 'hp' , int(character['hp'])  )
            self.hset(key, 'max_hp' , int(character['max_hp'])  )
            self.hset(key, 'sanity' , int(character['sanity'])  )
            self.hset(key, 'max_sanity' , int(character['max_sanity'])  )
            self.hset(key, 'attack' , int(character['attack'])  )
            self.hset(key, 'defense' , int(character['defense'])  )
            self.hset(key, 'magic' , int(character['magic'])  )
            self.hset(key, 'inventory' , character['inventory']  )
            self.hset(key, 'npc' , character['npc']  )
            self.hset(key, 'deep_level' , character['deep_level']  )
            self.hset(key, 'alter_ego' , character['alter_ego']  )
            self.hset(key, 'alter_subego' , character['alter_subego']  )
            self.hset(key, 'respawn' , int(character['respawn'])  )
            self.hset(key, 'pending_reborn' , character['pending_reborn']  )
            self.hset(key, 'hours_recovered' , int(character['hours_recovered'])  )
            self.hset(key, 'description' , character['description']  )
            self.redis_client.expire(name=key, time=expiry_seconds)
            #sets
            set_name = self.get_cache_key('sets', 'all') 
            self.ssad(set_name, key )
            self.redis_client.expire(name=set_name, time=expiry_seconds)
            return True
        except Exception as e:
            print(f"Error setting Redis key {key}: {str(e)}")
            return False

    def adjust_character(self, clean_data):
        try:
            clean_data["inventory"] = json.loads(clean_data["inventory"])   # string -> list
            clean_data["alter_subego"] = json.loads(clean_data["alter_subego"]) if clean_data["alter_subego"] else None
            clean_data["pending_reborn"] = None if clean_data["pending_reborn"] == "null" else clean_data["pending_reborn"]
            clean_data["npc"] = clean_data["npc"] == "true"
            clean_data["status"] = clean_data["status"].replace('"','')
            clean_data["alter_ego"] = clean_data["alter_ego"].replace('"','')
            clean_data["deep_level"] = clean_data["deep_level"].replace('"','')
            clean_data["name"] = clean_data["name"].replace('"','')
            clean_data["description"] = clean_data["description"].replace('"','')
            clean_data["picture"] = clean_data["picture"].replace('"','')
            clean_data["id"] = clean_data["id"].replace('"','')
            clean_data["notionid"] = clean_data["notionid"].replace('"','')
            clean_data['hours_recovered'] = int(clean_data['hours_recovered'])
            clean_data['respawn'] = int(clean_data['respawn'])
            clean_data['level'] = int(clean_data['level'])
            clean_data['coins'] = float(clean_data['coins'])
            clean_data['xp'] = int(clean_data['xp'])
            clean_data['max_xp'] = int(clean_data['max_xp'])
            clean_data['hp'] = int(clean_data['hp'])
            clean_data['max_hp'] = int(clean_data['max_hp'])
            clean_data['sanity'] = int(clean_data['sanity'])
            clean_data['max_sanity'] = int(clean_data['max_sanity'])
            clean_data['attack'] = int(clean_data['attack'])
            clean_data['defense'] = int(clean_data['defense'])
            clean_data['magic'] = int(clean_data['magic'])
            return clean_data
        except Exception as e:
            print(f"Error ajusting -> {clean_data} | Error in {str(e)}")
            return None

    def hscan(self, name, match, count=100):
        try:
            result = self.redis_client.hscan(name=name, match=match, count=count)
            print(f"hscan({name}, {match}, {count}) ? { result }")
            return result
        except Exception as e:
            print(f"Error hscan({name}, {match}): {str(e)}")
            return None


    def set_index(self, prefix ):
        try:
            hashIndexCreated = self.redis_client.ft("idx:"+prefix)
            if not hashIndexCreated:
                hashSchema = (
                    TextField("name"),
                    TextField("deep_level"),
                    TextField("status")
                )

                hashIndexCreated = self.redis_client.ft("idx:"+prefix).create_index(
                    hashSchema,
                    definition=IndexDefinition(
                        prefix=[prefix], index_type=IndexType.HASH
                    )
                )   
            return hashIndexCreated
        except Exception as e:
            print(f"Error set_index : {str(e)}")
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

    def query_characters_by_deep_status(self, prefix, deep_level=None, status=None):
        matching_characters = []
        try:
            qry = "@deep_level:"+deep_level if deep_level else ''
            qry += (' & ' if len(qry) > 0 else '') + "@status:"+status if status else ''
            findHashResult = self.redis_client.ft("idx:"+prefix).search(Query(qry).paging(0,self.limit_redis_results))
            total = self.redis_client.ft("idx:"+prefix).search(Query(qry).paging(0,self.limit_redis_results)).total
            for doc in findHashResult.docs:
                data = doc.__dict__
                clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
                adjusted = self.adjust_character(clean_data)
                matching_characters.append(adjusted)  
            print(f"🚻 Returning {len(matching_characters)} characters out of {total}. qry={qry} paging {self.limit_redis_results}")
        except Exception as e:
            print(f"❌ Error querying characters: {str(e)}")
        
        return matching_characters   


    def query_habits(self, field, value):
        """
        Query habits based on a specific field and value.
        
        Args:
            field (str): The field to query (e.g., 'name', 'deeplevel').
            value (str): The value to match against the field.
        
        Returns:
            list: A list of habits  that match the query.
        """
        matching_habits = []
        try:
            # Get all keys that match the habit pattern
            keys = self.redis_client.keys("rpg:habits:*")
            
            for key in keys:
                # Get habit data and convert it to a dictionary
                habit_data = self.redis_client.get(key)
                if habit_data:
                    habit_data = json.loads(habit_data)  
                    if habit_data and habit_data[field] == (value):
                        matching_habits.append(habit_data)  
            
            print(f"✅ Found {len(matching_habits)} matching habits for {field} = {value}.")
        except Exception as e:
            print(f"❌ Error querying habits: {str(e)}")
        
        return matching_habits    

    def query_tournaments(self, field, value):
        """
        Query tournaments based on a specific field and value.
        
        Args:
            field (str): The field to query (e.g., 'name', 'deeplevel').
            value (str): The value to match against the field.
        
        Returns:
            list: A list of tournaments  that match the query.
        """
        matching_tournaments = []
        try:
            # Get all keys that match the habit pattern
            keys = self.redis_client.keys("rpg:tournaments:*")
            
            for key in keys:
                # Get habit data and convert it to a dictionary
                tournament_data = self.redis_client.get(key)
                if tournament_data:
                    tournament_data = json.loads(tournament_data)  
                    if tournament_data and tournament_data[field] == (value):
                        matching_tournaments.append(tournament_data)  
            
            print(f"✅ Found {len(matching_tournaments)} matching tournaments for {field} = {value}.")
        except Exception as e:
            print(f"❌ Error querying tournaments: {str(e)}")
        
        return matching_tournaments        

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