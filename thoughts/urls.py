from django.urls import path
from . import views

urlpatterns = [
    # Thought endpoints
    path('ai_conversation', views.ai_conversation, name='ai_conversation'),
    path('conversation', views.conversation, name='conversation'),
    path('create_conversation', views.create_conversation, name='create_conversation'),
]