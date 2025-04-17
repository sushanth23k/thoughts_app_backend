import os
import redis
from dotenv import load_dotenv

def get_redis_connection():
    """
    Establishes a connection to Redis using credentials from environment variables
    Returns:
        Redis: Redis client instance
    """
    try:
        # Create Redis client
        redis_client = redis.Redis(
            host=os.getenv('redis_host'),
            port=os.getenv('redis_port'),
            password=os.getenv('redis_password'),
            decode_responses=True
        )
        
        # Test connection
        redis_client.ping()
        print("Successfully connected to Redis!")
        
        return redis_client
        
    except Exception as e:
        print(f"Error connecting to Redis: {str(e)}")
        raise

if __name__ == "__main__":
    redis_client = get_redis_connection()
    print("Redis connection test successful")
