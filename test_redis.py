from backend.services.redis_service import RedisService
from dotenv import load_dotenv

def test_redis_connection():
    try:
        redis_service = RedisService()
        
        # Test basic operations
        redis_service.set_with_expiry('test_key', {'message': 'Hello Redis Cloud!'}, 0.2 )
        result = redis_service.get('test_key')
        print("Test Result:", result)
        
        # Get connection info
        connection_info = redis_service.get_connection_info()
        print("Redis Connection Info:", connection_info)
        
        return True
    except Exception as e:
        print(f"Redis Cloud test failed: {str(e)}")
        return False

# Run test
if __name__ == "__main__":
    load_dotenv()
    test_redis_connection()