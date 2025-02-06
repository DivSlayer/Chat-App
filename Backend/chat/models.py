from django.db import models

from Client.models import Client


class Room(models.Model):
    room_name = models.CharField(max_length=50)

    def __str__(self):
        return self.room_name





class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(Client, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    message_type = models.CharField(max_length=10, default='text')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{str(self.room)} - {self.sender}"
