from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('communityservice.urls')),
    path("chat/", include('chat.urls', namespace='chat')),
    path('admin/', admin.site.urls),
]