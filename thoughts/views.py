from rest_framework.decorators import api_view
from rest_framework.response import Response
import redis
import json
import sys
sys.path.append("..")
from components.conversation_component import ConversationComponent


# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)


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
