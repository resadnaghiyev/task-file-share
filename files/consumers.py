import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from accounts.models import User
from .serializers import ChatTimeSerializer
from .models import Comment
from .service import *


class ChatConsumer(WebsocketConsumer):

    def fetch_comments(self, data):
        comments = get_last_20_comments(
            data['fileId'], data['username'], data['from']
        )
        s = ChatTimeSerializer(comments, many=True)
        content = {
            'command': 'comments',
            'comments': s.data
        }
        self.send_message(content)
    
    def new_comment(self, data):
        username = data['username']
        req_username = data['from']
        file_id = data['fileId']
        content = data['comment']
        comment = create_comment(
            username, req_username, file_id, content
        )
        comment.save()
        s = CommentSerializer(comment)
        content = {
            'command': 'new_comment',
            'comment': s.data
        }
        return self.send_chat_message(content)

    commands = {
        'fetch_comments': fetch_comments,
        'new_comment': new_comment
    }

    def connect(self):
        self.file_id = self.scope['url_route']['kwargs']['file_id']
        self.file_group_name = 'api_file_%s' % self.file_id 
        async_to_sync(self.channel_layer.group_add)(
            self.file_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.file_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)
    
    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.file_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    
    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
