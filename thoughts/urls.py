from django.urls import path
from . import views

urlpatterns = [
    # Thought endpoints
    # path('ai_conversation', views.ai_conversation, name='ai_conversation'),
    path('get_conversation', views.get_conversation, name='get_conversation'),
    path('create_conversation', views.create_conversation, name='create_conversation'),
    path('store_cache_conversation', views.store_cache_conversation, name='store_cache_conversation'),
    path('get_cache_conversation', views.get_cache_conversation, name='get_cache_conversation'),
    path('llm_conversation', views.llm_conversation, name='llm_conversation'),
    path('tts', views.tts, name='tts'),
    path('start_conversation', views.start_conversation, name='start_conversation'),
    path('conversation_loop', views.conversation_loop, name='conversation_loop'),
    path('stop_conversation', views.stop_conversation, name='stop_conversation'),
]