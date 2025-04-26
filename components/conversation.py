import os
import sys
import groq
import redis
import json
import base64
import pyaudio
import wave
import asyncio
import deepgram
import random

# Import Components

from components import agent_info, cache_db, llm, tts, nosql_db

from dotenv import load_dotenv

load_dotenv()

class Conversation:

    def __init__(self, deepgram_client, groq_client, redis_client):
        self.deepgram_client = deepgram_client
        self.groq_client = groq_client
        self.redis_client = redis_client

    def start_conversation(self):

        try:
            # Get a random start message
            start_message = random.choice(agent_info.start_messages)

            # Get the audio bytes
            start_audio_bytes = asyncio.run(tts.text_to_speech(self.deepgram_client, start_message))

            # Create a new conversation
            conversation = {
                "agent": start_message
            }
            conversation_id = nosql_db.new_conversation(self.db, conversation)

            # Create a new conversation in Redis
            cache_db.new_conversation(self.redis_client, conversation_id, conversation)

            # Convert the audio bytes to base64
            start_audio_base64 = base64.b64encode(start_audio_bytes).decode('utf-8')

            message = {
                "role": "agent",
                "content": start_message,
                "voice": start_audio_base64,
                "conversation_id": conversation_id
            }

            return message
        
        except Exception as e:
            print(f"Error starting conversation: {e}")
            return None

    def conversation_loop(self, conversation_id, user_message):
        try:
            # Get the conversation from Redis and append the user message
            conversation = cache_db.get_conversation(self.redis_client, conversation_id)
            conversation.append({"role": "user", "content": user_message})

            # Get the thoughts from Redis
            thoughts = cache_db.get_thoughts(self.redis_client, conversation_id)

            # Get the conversation memory
            conversation_memory = llm.get_conversation_memory(self.redis_client, conversation)

            # Get the AI response
            ai_response = llm.get_ai_response(self.groq_client, conversation_memory, thoughts)

            # Append the AI response to the conversation and store in Redis
            conversation.append({"role": "agent", "content": ai_response["response"]})
            cache_db.store_conversation(self.redis_client, conversation_id, conversation)

            # Check if the thoughts are different
            if ai_response["thoughts"] != thoughts:
                # Store the TTS response in Redis
                cache_db.store_thoughts(self.redis_client, conversation_id, ai_response["thoughts"])
            
            return ai_response["response"]
        except Exception as e:
            print(f"Error in conversation loop: {e}")
            return None

    def end_conversation(self, conversation_id):
        try:
            # Get the conversation from Redis
            conversation = cache_db.get_conversation(self.redis_client, conversation_id)

            # Get the thoughts from Redis
            thoughts = cache_db.get_thoughts(self.redis_client, conversation_id)

            # Store the conversation in MongoDB
            nosql_db.store_conversation(self.db, conversation_id, conversation, thoughts)
            
        except Exception as e:
            print(f"Error in end_conversation: {e}")
            return None
        return "Conversation Ended"
