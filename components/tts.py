import asyncio
import json
import os
from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    SpeakWebSocketEvents,
    SpeakWSOptions,
)
import pyaudio
import wave
import io
from io import BytesIO

# Audio configuration
RATE = 16000  # Standard sample rate for speech

def get_deepgram_client():
    # Get Deepgram API key from environment variables
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    if not DEEPGRAM_API_KEY:
        raise ValueError("Deepgram API key not found. Please set DEEPGRAM_API_KEY environment variable.")
    
    # Create a deepgram client
    config = DeepgramClientOptions(
        options={"speaker_playback": "false"}
    )
    client = DeepgramClient(DEEPGRAM_API_KEY, config)
    
    # asyncio.run(text_to_speech(client, "Hello, how are you?"))
    print("Deepgram client Working")


    return client

async def text_to_speech(client, text: str) -> bytes:
    """
    Converts text to speech using Deepgram's WebSocket API and returns audio bytes
    Args:
        text (str): Text to convert to speech
    Returns:
        bytes: Audio data in WAV format
    """
    try:
        # Create audio bytes buffer
        audio_bytes = bytearray()
        
        # Create WebSocket connection
        dg_connection = client.speak.asyncwebsocket.v("1")
        
        # Set up event handlers
        async def on_audio_data(self, data, **kwargs):
            audio_bytes.extend(data)
            
        async def on_flush(self, flushed, **kwargs):
            print("Flushed")
            
        # Register event handlers
        dg_connection.on(SpeakWebSocketEvents.AudioData, on_audio_data)
        dg_connection.on(SpeakWebSocketEvents.Flushed, on_flush)
        
        # Create WebSocket options
        options = SpeakWSOptions(
            model="aura-asteria-en",
            encoding="linear16",
            sample_rate=RATE
        )
        
        # Start the connection
        if await dg_connection.start(options) is False:
            raise Exception("Failed to start WebSocket connection")
        
        # Send the text
        await dg_connection.send_text(text)
        print("Text sent to Deepgram")
        
        # Flush to get audio
        await dg_connection.flush()
        print("Flushed to Deepgram")
        
        # Wait for completion
        await dg_connection.wait_for_complete()
        print("Completed")
        
        # Close the connection
        await dg_connection.finish()
        
        return raw_pcm_to_wav(bytes(audio_bytes))
        
    except Exception as e:
        print(f"Error in text_to_speech: {str(e)}")
        raise

def raw_pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    """
    Convert raw PCM bytes to WAV format bytes with proper header.
    
    Args:
        pcm_bytes: Raw PCM audio data (16-bit little-endian)
        sample_rate: Sample rate in Hz (default 16000)
        channels: Number of audio channels (default 1)
    
    Returns:
        bytes: WAV file bytes
    """
    # Create a BytesIO object to hold the WAV data
    with BytesIO() as wav_buffer:
        with wave.open(wav_buffer, 'wb') as wav_file:
            # Set WAV parameters
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)  # 16-bit = 2 bytes
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_bytes)
        
        # Get the complete WAV bytes
        wav_bytes = wav_buffer.getvalue()
    
    return wav_bytes


def output_audio(wav_bytes, text):

    # Playing the audio and deleting it
    chunk = 1024  
    f = wave.open(io.BytesIO(wav_bytes),"rb")  
    p = pyaudio.PyAudio()  
    
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                rate = f.getframerate(),  
                channels=f.getnchannels(),
                output = True,
                frames_per_buffer=chunk)

    data = f.readframes(chunk)
    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  
    
    stream.stop_stream()  
    stream.close()    
    p.terminate()

    return text

# # Update the main test code to properly handle async operations
# if __name__ == "__main__":
#     # Test the text-to-speech functionality
#     test_text = "Hello! This is a test of the text to speech functionality."
    
#     # Create and run the event loop
#     asyncio.run(text_to_speech(test_text))
