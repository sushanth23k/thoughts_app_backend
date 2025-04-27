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
from groq import Groq
import langchain_groq
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq

# Import Components
from components import agent_info, cache_db, llm, tts, nosql_db

class Conversation:

    def __init__(self, deepgram_client, groq_client, redis_client, mg_client):
        self.deepgram_client = deepgram_client
        self.groq_client = groq_client
        self.redis_client = redis_client
        self.db = mg_client
        
        # Initialize the LLM
        os.environ["GROQ_API_KEY"] = os.getenv("groq_api")
        self.llm = ChatGroq(
            model=agent_info.llm_info["model"],
            temperature=agent_info.llm_info["temperature"],
            max_tokens=agent_info.llm_info["max_tokens"],
            timeout=agent_info.llm_info["timeout"],
            max_retries=agent_info.llm_info["max_retries"],
            model_kwargs={"response_format": agent_info.llm_info["response_format"]}
        )

    def start_conversation(self):

        try:
            # Get a random start message
            start_message = random.choice(agent_info.start_messages)

            # Get the audio bytes and convert to base64
            start_audio_bytes = asyncio.run(tts.text_to_speech(self.deepgram_client, start_message))
            start_audio_base64 = base64.b64encode(start_audio_bytes).decode('utf-8')

            # Create a new conversation
            conversation = [{
                "agent": start_message
            }]
            conversation_id = str(nosql_db.new_conversation(self.db, conversation))

            # Create a new conversation in Redis
            cache_db.new_conversation(self.redis_client, conversation_id, conversation)

            output = {
                "role": "agent",
                "content": start_message,
                "voice": start_audio_base64,
                "conversation_id": str(conversation_id)
            }

            return output
        
        except Exception as e:
            print(f"Error starting conversation: {e}")
            return None

    def conversation_loop(self, conversation_id, user_message):
        try:
            # Get the conversation from Redis and append the user message
            conversation = cache_db.get_conversation(self.redis_client, conversation_id)
            conversation.append({"user": user_message})

            # Get the thoughts from Redis
            thoughts = cache_db.get_thoughts(self.redis_client, conversation_id)

            # Get the conversation memory
            conversation_memory = self.get_conversation_memory(conversation)

            # Get the AI response
            ai_response = self.get_ai_response(conversation_memory, thoughts)

            # Append the AI response to the conversation and store in Redis
            conversation.append({"agent": ai_response["response"]})
            cache_db.store_conversation(self.redis_client, conversation_id, conversation)

            if ai_response["thoughts"] !=[]:
                # Store the thoughts in Redis
                for thought in ai_response["thoughts"]:
                    if thought not in thoughts:
                        thoughts.append(thought)
                asyncio.run(cache_db.store_thoughts(self.redis_client, conversation_id, thoughts))
            
            # Get the TTS response
            response_audio = asyncio.run(tts.text_to_speech(self.deepgram_client, ai_response["response"]))
            response_audio = base64.b64encode(response_audio).decode('utf-8')

            output = {
                "status": ai_response["status"],
                "response": ai_response["response"],
                "conversation_id": conversation_id,
                "thoughts": ai_response["thoughts"],
                "response_audio": response_audio
            }
            
            return output
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
            print(nosql_db.store_conversation(self.db, conversation_id, conversation, thoughts))
            
        except Exception as e:
            print(f"Error in end_conversation: {e}")
            return None
        return "Conversation Ended"

    def get_conversation_memory(self, conversation):
        """
        Generates a response from the LLM based on the conversation memory
        """
        conversation_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        for item in conversation:
            if "user" in item:
                conversation_memory.chat_memory.add_user_message(item["user"])
            else:
                conversation_memory.chat_memory.add_ai_message(item["agent"])

        return conversation_memory

    def get_ai_response(self, conversation_memory, thoughts):
        """
        Generates a response from the LLM based on the conversation data
        """
        # Get the system prompt
        system_prompt = agent_info.system_prompt.replace("{{thoughts}}", json.dumps(thoughts))

        # Get the messages
        messages = [
            {"role": "system", "content": system_prompt},
        ] + conversation_memory.chat_memory.messages

        count = 0
        while True:
            # Get the AI response
            try:
                ai_response = self.llm.invoke(messages, timeout=10)
                response = ai_response.content
                response = json.loads(response)
                break
            except Exception as e:
                print(f"Error in get_ai_response: {e}")
                count += 1
                if count > 3:
                    break
        # Return the AI response
        ai_response = {
            "status":response["status"],
            "response": response["response"],
            "thoughts": response["thoughts"]
        }
        return ai_response
