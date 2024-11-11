# chat/models.py
from django.contrib.auth.models import User
from django.db import models
from encrypted_model_fields.fields import EncryptedTextField
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = EncryptedTextField()  # Use encrypted field for message content
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']


class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, related_name='user1_rooms', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='user2_rooms', on_delete=models.CASCADE)

    def __str__(self):
        return f"ChatRoom between {self.user1.username} and {self.user2.username}"

    @staticmethod
    def get_room(user1, user2):
        return ChatRoom.objects.filter(user1=user1, user2=user2).first() or \
               ChatRoom.objects.filter(user1=user2, user2=user1).first()