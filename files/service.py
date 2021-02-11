from django.shortcuts import render, get_object_or_404
from accounts.models import User
from .models import *


def get_last_20_comments(fileId, username, req_username):
    file_obj = get_object_or_404(File, id=fileId)
    user = get_object_or_404(User, username=username)
    req_user = get_object_or_404(User, username=req_username)
    chat = Chat.objects.filter(
        file=file_obj, participants=user
    ).filter(participants=req_user).first()
    if chat:
        qs = ChatTime.objects.filter(chat=chat) \
            .order_by('-timestamp')[:20]
        return qs
    else:
        return 'not found'


def create_comment(username, req_username, file_id, content):
    chat = Chat.objects.filter(
        file__id=file_id, participants__username=username
    ).filter(participants__username=req_username).first()
    if chat:
        new_comment = Comment.objects.create(
            user__username=req_username,
            content=content,
        )
        chat.comments.add(new_comment)
        return new_comment
    else:
        return 'bad request'
