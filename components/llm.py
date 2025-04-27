import os
from groq import Groq
import langchain_groq

def get_groq_client():
    """
    Establishes a connection to Groq API using credentials from environment variables
    Returns:
        Groq: Groq client instance
    """
    try:
        # Get Groq API key from environment variables
        api_key = os.getenv('groq_api')
        
        if not api_key:
            raise ValueError("Groq API key not found in environment variables")
            
        # Create Groq client
        client = Groq(api_key=api_key)
        print("Successfully connected to Groq API!")
        
        return client
        
    except Exception as e:
        print(f"Error connecting to Groq API: {str(e)}")
        raise

def get_llm_response(client, conversation_data):
    """
    Generates a response from the LLM based on the conversation data
    Args:
        client (Groq): Groq client instance
        conversation_data (list): List of dictionaries containing conversation messages
    Returns:
        str: Response from the LLM
    """
    try:

        # Get response from LLM
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": conversation_data}
            ]
        )

        # Return response
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error getting LLM response: {str(e)}")
        raise

