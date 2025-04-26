import os
import redis
import json
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

def new_conversation(redis_client, conversation_id, conversation):
    """
    Creates a new conversation in Redis
    """
    redis_client.set(conversation_id, json.dumps(conversation))
    redis_client.set(conversation_id + "_thoughts", json.dumps([]))

    return conversation_id

def get_conversation(redis_client, conversation_id):
    """
    Retrieves a conversation from Redis
    """
    return redis_client.get(conversation_id)

def get_thoughts(redis_client, conversation_id):
    """
    Retrieves thoughts from Redis
    """
    return redis_client.get(conversation_id + "_thoughts")

def store_conversation(redis_client, conversation_id, conversation):
    """
    Stores a conversation in Redis
    """
    redis_client.set(conversation_id, json.dumps(conversation))

def store_thoughts(redis_client, conversation_id, thoughts):
    """
    Stores thoughts in Redis
    """
    redis_client.set(conversation_id + "_thoughts", json.dumps(thoughts))


if __name__ == "__main__":
    redis_client = get_redis_connection()
    print("Redis connection test successful")
