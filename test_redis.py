from redis import cache
from backend.services import redis_service
from backend.services.redis_service import RedisService


def test_redis_connection():
    try:
        redis_service = RedisService()
        
        # Test basic operations
        redis_service.set_with_expiry('test_key', {'message': 'Hello Redis Cloud!'}, 0.1 )
        result = redis_service.get('test_key')
        print("Test Result:", result)
        
        # Get connection info
        connection_info = redis_service.get_connection_info()
        print("Redis Connection Info:", connection_info)

        #what_we_got = redis_service.get_smembers('sample_restaurant:*')
        #print("WwGoT::: ", what_we_got)

        #redis_service.ssad('tournament:'+'test_tournament'
        #                , {'message': 'Hello Redis Cloud!', 'sacapa': [ {"a": False},{"b": True} ]})
        
        return True
    except Exception as e:
        print(f"Redis Cloud test failed: {str(e)}")
        return False


def test_insert_as_set(character_id):
    try:
        redis_service = RedisService()
        cache_key_from = redis_service.get_cache_key('characters', character_id)
        cache_key_to = redis_service.get_cache_key('cryptids', character_id)
        character = redis_service.get(cache_key_from)
        #print(character)
        if character:
            redis_service.hset(cache_key_to, 'name' , character['name']  )
            redis_service.hset(cache_key_to, 'status' , character['status']  )
            redis_service.hset(cache_key_to, 'picture' , character['picture']  )
            redis_service.hset(cache_key_to, 'level' , character['level']  )
            redis_service.hset(cache_key_to, 'coins' , character['coins']  )
            redis_service.hset(cache_key_to, 'xp' , character['xp']  )
            redis_service.hset(cache_key_to, 'max_xp' , character['max_xp']  )
            redis_service.hset(cache_key_to, 'hp' , character['hp']  )
            redis_service.hset(cache_key_to, 'max_hp' , character['max_hp']  )
            redis_service.hset(cache_key_to, 'sanity' , character['sanity']  )
            redis_service.hset(cache_key_to, 'max_sanity' , character['max_sanity']  )
            redis_service.hset(cache_key_to, 'attack' , character['attack']  )
            redis_service.hset(cache_key_to, 'defense' , character['defense']  )
            redis_service.hset(cache_key_to, 'magic' , character['magic']  )
            redis_service.hset(cache_key_to, 'inventory' , character['inventory']  )
            redis_service.hset(cache_key_to, 'npc' , character['npc']  )
            redis_service.hset(cache_key_to, 'deep_level' , character['deep_level']  )
            redis_service.hset(cache_key_to, 'alter_ego' , character['alter_ego']  )
            redis_service.hset(cache_key_to, 'alter_subego' , character['alter_subego']  )
            redis_service.hset(cache_key_to, 'respawn' , character['respawn']  )
            redis_service.hset(cache_key_to, 'pending_reborn' , character['pending_reborn']  )
            redis_service.hset(cache_key_to, 'hours_recovered' , character['hours_recovered']  )
            redis_service.hset(cache_key_to, 'description' , character['description']  )
            
            redis_service.ssad(redis_service.get_cache_key('cryptids:sets', 'all') , cache_key_to)
            #redis_service.ssad(redis_service.get_cache_key('cryptids:sets', character['status']) , cache_key_to)
            #redis_service.ssad(redis_service.get_cache_key('cryptids:sets', character['deep_level']) , cache_key_to)
            redis_service.ssad(redis_service.get_cache_key('cryptids:sets', character['deep_level'] + ':' + character['status']) , cache_key_to)

            redis_service.set_index(redis_service.get_cache_key('cryptids') ) 
    except Exception as e:
        print(f"Redis Cloud test failed: {str(e)}")
        return False

def test_hscan(name, pattern):
    try:
        redis_service = RedisService()
        result = redis_service.hscan(name, pattern)
        print("Test Result:", result)
    except Exception as e:
        print(f"Redis Cloud test failed: {str(e)}")
        return False

def test_sscan(name, pattern):
    try:
        redis_service = RedisService()
        result = redis_service.sscan(name, pattern)
        print("Test Result:", result)
    except Exception as e:
        print(f"Redis Cloud test failed: {str(e)}")
        return False

def query_characters_by_deep_status( prefix, deep_level=None, status=None):
    try:
        redis_service = RedisService()
        result = redis_service.query_characters_by_deep_status(prefix=prefix, deep_level=deep_level, status=status)
        #print("Test Result:", result)
    except Exception as e:
        print(f"Redis Cloud test failed: {str(e)}")
        return False

def test_query( ):
    try:
        redis_service = RedisService()
        result = redis_service.query_characters('deep_level','l2')
        print(result)
    except Exception as e:
        print(f"Redis Cloud test failed: {str(e)}")
        return False

# Run test
if __name__ == "__main__":
    print("🍎_🍏")
    #test_redis_connection()
    #test_insert_as_set('150a3d23499280c98bc7c6a602ee96d4')
    #test_insert_as_set('0a819f70cdc44095a94d3c7dc1a724c8')
    #test_insert_as_set('122a3d2349928020ab78ccdc6aab747d')
    #test_sscan('rpg:cryptids:sets:l1','high*')
    query_characters_by_deep_status( 'rpg:cryptids:', deep_level='l2')
    #query_characters_by_deep_status( 'rpg:cryptids:', status='dead')
    #test_query()
