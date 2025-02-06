# serializers.py
from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    own = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None

    def get_own(self, obj):
        ip = self.context.get('ip', None)
        if ip is not None:
            return ip == obj.sender.ip
        return False

    def get_sender(self, obj):
        return obj.sender.name

    class Meta:
        model = Message
        fields = ['sender', 'message', 'file_url', 'message_type', 'created_at', 'file_name', 'own']
