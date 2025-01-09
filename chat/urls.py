from django.urls import path
from .views import chat_view

app_name = 'chat'

urlpatterns = [
    path('<str:group_name>/', chat_view, name="chat"),
]