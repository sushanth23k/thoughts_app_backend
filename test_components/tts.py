import httpx
import threading
import asyncio
from dotenv import load_dotenv
import os

from deepgram.utils import verboselogs

from deepgram import (
    DeepgramClient,
    ClientOptionsFromEnv,
    SpeakOptions,
)

# Load environment variables
load_dotenv()

def get_deepgram_client():
    """
    Establishes a connection to Deepgram API using credentials from environment variables
    Returns:
        DeepgramClient: Deepgram client instance
    """
    try:
        # Get Deepgram API key from environment variables
        DEEPGRAM_API_KEY = os.getenv('deepgram_api')

        # Create Deepgram client
        client = DeepgramClient(DEEPGRAM_API_KEY)
        print("Successfully connected to Deepgram API!")
        return client
    
    except Exception as e:
        print(f"Error getting Deepgram client: {str(e)}")
        raise



if __name__ == "__main__":
    deepgram_client = get_deepgram_client()
    print("Deepgram API connection test successful")
