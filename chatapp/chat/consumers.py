# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, User, UserProfile
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_username = self.scope['url_route']['kwargs']['username']
        sender_username = self.scope["user"].username
        # Sort the usernames alphabetically to ensure a consistent group name
        usernames = sorted([sender_username, self.receiver_username])
        # Create a sanitized room name
        self.room_name = f'chat_{usernames[0]}_{usernames[1]}'
        self.room_name = self.room_name.replace('@', '_').replace('.', '_')
        
        # Define the group name for Channels
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Notify others in the room that the user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'status': 'online',
                'username': sender_username
            }
        )
        logger.info(f"User {self.scope['user']} connected to {self.room_group_name}")
        await self.accept()
        # Notify that the user has gone online
        await self.update_online_status(True)

    async def disconnect(self, close_code):
        # Notify that the user has gone offline
        await self.update_online_status(False)
        # Notify others in the room that the user is offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'status': 'offline',
                'username': self.scope["user"].username
            }
        )
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.scope['user']} disconnected from {self.room_group_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.save_message(self.scope["user"], self.receiver_username, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.scope["user"].username,
            }
        )
        logger.info(f"Message sent: {message} from {self.scope['user']}")

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
            'sender': sender,
        }))
        logger.info(f"Message received in {self.room_group_name}: {event['message']}")

    async def user_status(self, event):
        # Log the user status change
        logger.info(f"User {event['username']} is now {event['status']} in group {self.room_group_name}")
        # Handles online/offline status events
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'username': event['username'],
        }))
        

    @sync_to_async
    def save_message(self, sender, receiver_username, content):
        receiver = User.objects.get(username=receiver_username)
        Message.objects.create(sender=sender, receiver=receiver, content=content)

    @sync_to_async
    def update_online_status(self, is_online):
        profile, created = UserProfile.objects.get_or_create(user=self.scope["user"])
        profile.is_online = is_online
        profile.save()
