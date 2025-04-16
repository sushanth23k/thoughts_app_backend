from rest_framework.decorators import api_view
from rest_framework.response import Response
import redis
import json
import sys
sys.path.append("..")
from components.conversation_component import ConversationComponent

# Components
from test_components import nosql_db


# Initialize MongoDB connection
# mg_client = nosql_db.get_mongodb_connection()

# Initialize Redis connection
# redis_client = redis.Redis(host='localhost', port=6379, db=0)


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
def conversation(request):
    try:
        # Get MongoDB client and collection
        conv_collection = mg_client.get_collection('conversations')

        # Get conversation
        conversation = conv_collection.find({"conversation_id": request.data.get('conversation_id')})

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
        conv_collection = mg_client['conversations']

        # Create conversation
        conversation = conv_collection.insert_one({"messages": messages})

        mg_client.close()

        # Return conversation ID
        return Response({"conversation_id": str(conversation.inserted_id)})
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=500)
    
    