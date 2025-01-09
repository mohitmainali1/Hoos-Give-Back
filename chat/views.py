from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from communityservice.models import Project
from .forms import *

@login_required
def chat_view(request, group_name):
    user = request.user
    project = get_object_or_404(Project, title=group_name)
    chat_group = get_object_or_404(ChatGroup, group_name=group_name)
    project_id = project.id
    chat_messages = chat_group.chat_messages.all()[:10]
    form = GroupMessageForm()

    if request.htmx:
        form = GroupMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                'message' : message,
                'user' : request.user,
            }
            return render(request, 'chat/partials/chat_message_p.html', context)

    return render(request, 'chat/chat.html', {'group_name' : group_name, 'chat_messages' : chat_messages, 'form' : form, 'project_id' : project_id, 'user' : user, 'project' : project})