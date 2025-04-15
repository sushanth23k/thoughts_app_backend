from components.llm_component import AIConversation
from components.redis_component import RedisConversationStore
from langchain.memory import ConversationBufferMemory
from typing import Dict, List, Any, Optional
import logging
import json

class ConversationComponent:
    def __init__(self):
        """Initialize conversation component with AI and Redis storage."""
        try:
            self.redis_component = RedisConversationStore()
        except Exception as e:
            logging.error(f"Failed to initialize ConversationComponent: {str(e)}")
            raise

    def process_message(self, message: str, conversation_id: str) -> Dict[str, Any]:
        """
        Process a user message within a conversation context.
        """
        try:
            self.llm_component = AIConversation()
            previous_thoughts = []
            # Retrieve existing conversation or create new one
            try:
                redis_data = self.redis_component.retrieve_conversation(conversation_id)
            except Exception as e:
                logging.error(f"Failed to retrieve conversation {conversation_id}: {str(e)}")
                raise ValueError(f"Could not access conversation data: {str(e)}")
            
            if redis_data is None:
                # Initialize new conversation
                conversation_data = [
                    {"ai": json.dumps({"reply": "Hi how can I help you today?", "thoughts": []})}
                ]
            else:
                conversation_data = redis_data
                previous_thoughts = self.redis_component.retrieve_thoughts(conversation_id)
           
            # Create memory from conversation history
            try:
                memory = ConversationBufferMemory(return_messages=True)
                for entry in conversation_data:
                    if "ai" in entry:
                        memory.chat_memory.add_ai_message(entry["ai"])
                    elif "human" in entry:
                        memory.chat_memory.add_user_message(entry["human"])
            except Exception as e:
                logging.error(f"Failed to create conversation memory: {str(e)}")
                raise ValueError(f"Error processing conversation history: {str(e)}")
            
            # Process the message with LLM
            try:
                self.llm_component.memory = memory
                response = self.llm_component.process_message(message, previous_thoughts)
            except Exception as e:
                logging.error(f"LLM processing failed: {str(e)}")
                raise ValueError(f"AI processing error: {str(e)}")
            
            if response.get('thoughts') !=[]:
                # Combine previous and new thoughts, removing duplicates
                combined_thoughts = list(set(previous_thoughts + response.get('thoughts', [])))
            else:
                combined_thoughts = previous_thoughts
            
            conversation_data.append({"human": message})
            conversation_data.append({"ai": json.dumps(response)})
            
            # Store and return results
            try:
                storage_success = self.redis_component.store_conversation(
                    conversation_id, 
                    conversation_data
                )
                self.redis_component.store_thoughts(conversation_id, combined_thoughts)
            except Exception as e:
                logging.error(f"Failed to store conversation {conversation_id}: {str(e)}")
                storage_success = False
            
            return {
                "success": storage_success,
                "response": response.get('reply', ''),
                "thoughts": combined_thoughts
            }
        except Exception as e:
            logging.error(f"Unexpected error in process_message: {str(e)}")
            return {
                "success": False,
                "response": "I'm sorry, but I encountered an error processing your message.",
                "error": str(e),
                "thoughts": []
            }