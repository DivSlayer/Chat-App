import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile

from Client.models import Client
from .models import Room, Message
from .serializers import MessageSerializer

ALLOWED_TYPES = ['jpeg', 'jpg', 'png', 'doc', 'docx', 'pptp', 'pptpx', 'pdf']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        self.room_name = f"main_room"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.remove_client()
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.close(code)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data_json = json.loads(text_data)
            sender_name = data_json['sender']
            # Call the synchronous function to get or create the sender
            await self.update_sender_name(sender_name)
            msg = await self.create_message(data=data_json)
            event = {"type": "send_message", "message": data_json, 'msg': msg, "ip": self.get_user_ip()}
            await self.channel_layer.group_send(self.room_name, event)
        elif bytes_data:
            # Handle binary data (if needed)
            pass

    @database_sync_to_async
    def update_sender_name(self, sender_name):
        user_ip = self.get_user_ip()  # Get the user IP
        sender = Client.objects.filter(ip=user_ip)

        if sender.exists():
            sender = sender[0]
            sender.name = sender_name
            sender.status = 0
            sender.save()

    @database_sync_to_async
    def remove_client(self):
        address = f"{self.scope['client'][0]}"
        client = Client.objects.filter(ip=address)
        if len(client) > 0:
            client = client.first()
            client.status = 1
            client.save()

    def get_user_ip(self):
        # This will return the IP address of the client
        return f"{self.scope['client'][0]}"

    async def send_message(self, event):
        msg = event["msg"]
        msg['own'] = event['ip'] == self.scope["client"][0]
        if msg is not None:
            await self.send(text_data=json.dumps({"message": msg}))

    @database_sync_to_async
    def create_message(self, data):
        try:
            name = data['sender']
            sender = Client.objects.filter(ip=self.get_user_ip())
            if len(sender):
                sender = sender.first()
            else:
                sender = Client.objects.create(ip=self.get_user_ip(), name=name)
                sender.save()
            sender.status = 0
            sender.save()
            get_room = Room.objects.get(room_name='main_room')
            message_type = data.get("message_type", "text")
            if message_type == "file":
                file_name = data['file_name']
                msgs = Message.objects.all()
                file_msg = None
                for msg in msgs:
                    if msg.file.name.split('/')[-1] == file_name:
                        file_msg = msg
                        break
                return MessageSerializer(file_msg, context={'ip': self.get_user_ip()}).data
            else:

                if not Message.objects.filter(
                        message=data["message"], sender__ip=sender.ip,
                ).exists():
                    msg = Message.objects.create(
                        room=get_room,
                        message=data["message"],
                        sender=sender,
                        message_type="text",
                    )
                    msg.save()
                    return MessageSerializer(msg, context={'ip': self.get_user_ip()}).data
            return None

        except Room.DoesNotExist:
            room = Room.objects.create(
                room_name='main_room',
            )
            room.save()
            self.create_message(data=data)
