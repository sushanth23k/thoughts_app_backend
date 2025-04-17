# APIs for the thoughts app

# Import Django Libraries
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Import Basic Libraries
import json
import sys

# Import Components
sys.path.append("..")
from components.conversation_component import ConversationComponent
from test_components.cache_db import get_redis_connection
from test_components.llm import get_groq_client, get_llm_response

# Import MongoDB connection
from django.db import connections
from bson.objectid import ObjectId

# Initialize MongoDB connection
mg_client = connections['default']

# Initialize Redis connection
redis_client = get_redis_connection()

# Initialize Groq client
groq_client = get_groq_client()

# AI Conversation
@api_view(['POST'])
def ai_conversation(request):
    try:
        # Get and validate required parameters
        conversation_id = request.data.get('conversation_id')
        message = request.data.get('message')
        
        if not conversation_id or not message:
            return Response({
                "error": "Both conversation_id and message are required"
            }, status=400)
           
        conversation_component = ConversationComponent()
        response = conversation_component.process_message(message, conversation_id)
        
        return Response(response)
        
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=500)


@api_view(['GET'])
def get_conversation(request):
    try:
        # Get MongoDB client and collection
        conv_collection = mg_client.get_collection('conversations')
        conversation_id = request.GET.get('conversation_id')

        # Get conversation
        conversation = conv_collection.find_one({"_id": ObjectId(conversation_id)})
        conversation["_id"] = str(conversation["_id"])

        # Return conversation
        return Response(conversation)
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=500)
    

@api_view(['POST'])
def create_conversation(request):
    try:
        # Get messages
        messages = request.data
        print(messages)

        # Get MongoDB client and collection
        conv_collection = mg_client.get_collection('conversations')

        # Create conversation
        conversation = conv_collection.insert_one({"messages": messages})

        # Return conversation ID
        return Response({"conversation_id": str(conversation.inserted_id)})
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=500)


@api_view(['POST'])
def store_cache_conversation(request):
    try:
        # Get conversation ID
        input_data = request.data

        conversation_id = input_data.get('conversation_id')
        conversation_data = input_data.get('conversation')

        # Store conversation data in Redis with conversation_id as key
        redis_client.set(conversation_id, json.dumps(conversation_data))

        # Return success
        return Response({"success": True})
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=500)
        
@api_view(['GET'])
def get_cache_conversation(request):
    try:
        # Get conversation ID
        conversation_id = request.GET.get('conversation_id')

        # Get conversation data from Redis
        conversation_data = redis_client.get(conversation_id)
        print(conversation_data)

        # Return conversation data
        return Response({"conversation_data": json.loads(conversation_data)})
    
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=500)

@api_view(['POST'])
def llm_conversation(request):
    try:
        # Get conversation ID
        input_data = request.data

        # Get LLM response
        llm_response = get_llm_response(groq_client, input_data["input"])
        print(llm_response)

        # Return LLM response
        return Response({"llm_response": llm_response})
    
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=500)

