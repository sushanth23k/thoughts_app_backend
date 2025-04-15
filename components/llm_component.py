import os
import logging
import json
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field

class ThoughtResponse(BaseModel):
    reply: str = Field(description="The response to continue the conversation")
    thoughts: List[str] = Field(description="List of thoughts extracted from the conversation")

class AIConversation:
    def __init__(self):
        """Initialize the AI conversation component with Groq LLM."""
        try:
            self.api_key = os.environ.get("GROQ_API_KEY")
            if not self.api_key:
                raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass it directly.")
            
            # Initialize the Groq LLM
            self.llm = ChatGroq(
                api_key=self.api_key,
                model_name="llama3-70b-8192",  # Using Llama 3 model
                temperature=0.7
            )
           
            # Create the output parser
            self.parser = JsonOutputParser(pydantic_object=ThoughtResponse)
            
            # Initialize conversation memory
            self.memory = ConversationBufferMemory(return_messages=True)
            
            # Create the prompt template
            self.prompt = ChatPromptTemplate.from_template("""
            You are a thoughtful assistant designed to have conversations with users and extract their thoughts.
            
            Your goal is to engage in a natural conversation while identifying distinct thoughts expressed by the user.
            If a thought seems complex or unclear, ask a simple clarifying question.
            
            Important instructions:
            - After collecting 2-3 thoughts from the user, end the conversation with "Thank you for sharing your thoughts. Have a wonderful day."
            - If the user indicates they want to end the conversation (with phrases like "That's all", "I'm done", etc.), 
              end the conversation with "Thank you for sharing your thoughts. Have a wonderful day." even if no thoughts were collected.
            
            Previous thoughts collected: {previous_thoughts}
            
            User's message: {user_message}
            
            Respond in a conversational manner and extract any thoughts the user has expressed.
            Format your response as a JSON object with the following structure:
            {{
                "reply": "Your response to continue the conversation or the ending message",
                "thoughts": ["Thought 1 as a complete sentence", "Thought 2 as a complete sentence"]
            }}
            
            If no clear thoughts are expressed, provide an empty list for thoughts.
            Only include new thoughts that are not already in the previous thoughts list.
            """)
            
            # Create the conversation chain
            self.chain = (
                self.prompt 
                | self.llm 
                | self.parser
            )
        except Exception as e:
            logging.error(f"Failed to initialize AIConversation: {str(e)}")
            raise
  
    def process_message(self, user_message, previous_thoughts=None):
        """
        Process a user message and generate a response.
        
        Args:
            user_message (str): The user's input message
            previous_thoughts (list): List of previously extracted thoughts
            
        Returns:
            ThoughtResponse: An object containing the AI reply and extracted thoughts
        """
        if previous_thoughts is None:
            previous_thoughts = []
        
        # Add the user message to memory
        self.memory.chat_memory.add_user_message(user_message)
       
        # Get the response using the chain
        response = self.chain.invoke({
            "user_message": user_message,
            "previous_thoughts": previous_thoughts
        })

        # Add the assistant response to memory
        self.memory.chat_memory.add_ai_message(json.dumps(response))
        
        return response
