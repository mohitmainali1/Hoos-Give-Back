# REFERENCES
# Title: Basic Setup with Htmx - Real-Time Chat app - Part 2
# Author: Andreas Jud
# URL: https://www.youtube.com/watch?v=Q7N2oJTnThA&list=PL5E1F5cTSTtRSP3Qb8-gZ-Hm5AXp3VKvu&index=2
from django.db import models
from communityservice.models import CustomUser

class ChatGroup(models.Model):
    group_name = models.CharField(unique=True)

    def __str__(self):
        return self.group_name

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    body = models.CharField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} : {self.body}'

    class Meta:
        ordering = ['-created']