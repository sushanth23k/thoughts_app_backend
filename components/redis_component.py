import redis
import json
import logging
from typing import Dict, List, Any, Optional
import os

class RedisConversationStore:
    """
    A component to store and retrieve conversation data from Redis.
    """
    
    def __init__(self):
        host = os.getenv('REDIS_HOST')
        port = os.getenv('REDIS_PORT')
        db = os.getenv('REDIS_DB')
        """
        Initialize the Redis connection.
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    def store_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]) -> bool:
        """
        Store conversation data in Redis.
        """
        try:
            # Convert the data to JSON string
            json_data = json.dumps(conversation_data)
            
            # Store in Redis with the conversation_id as key
            self.redis_client.set(conversation_id, json_data)
            return True
        except Exception as e:
            print(f"Error storing conversation: {str(e)}")
            return False
    
    def retrieve_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation data from Redis.
        """
        try:
            # Get data from Redis
            data = self.redis_client.get(conversation_id)
            
            if data:
                # Convert bytes to string and then to JSON
                return json.loads(data.decode('utf-8'))
            else:
                return None
        except Exception as e:
            print(f"Error retrieving conversation: {str(e)}")
            return None
    
    def store_thoughts(self, conversation_id: str, thoughts: List[str]) -> bool:
        """
        Store thoughts data in Redis.
        
        Args:
            conversation_id (str): The unique identifier for the conversation
            thoughts (List[str]): List of thoughts to store
            
        Returns:
            bool: True if storage was successful, False otherwise
        """
        try:
            # Create a key specifically for thoughts
            thoughts_key = f"{conversation_id}_thoughts"
            
            # Convert the thoughts list to JSON string
            json_data = json.dumps(thoughts)
            
            # Store in Redis with the thoughts_key
            self.redis_client.set(thoughts_key, json_data)
            return True
        except Exception as e:
            logging.error(f"Error storing thoughts: {str(e)}")
            return False
   
    def retrieve_thoughts(self, conversation_id: str) -> Optional[List[str]]:
        """
        Retrieve thoughts data from Redis.
        
        Args:
            conversation_id (str): The unique identifier for the conversation
            
        Returns:
            Optional[List[str]]: List of thoughts if found, None otherwise
        """
        try:
            # Create the key for thoughts
            thoughts_key = f"{conversation_id}_thoughts"
            
            # Get data from Redis
            data = self.redis_client.get(thoughts_key)
            
            if data:
                # Convert bytes to string and then to JSON
                return json.loads(data.decode('utf-8'))
            else:
                return None
        except Exception as e:
            logging.error(f"Error retrieving thoughts: {str(e)}")
            return None
