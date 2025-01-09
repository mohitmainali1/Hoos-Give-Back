from django.contrib import admin
from chat.models import ChatGroup, GroupMessage

admin.site.register(ChatGroup)
admin.site.register(GroupMessage)