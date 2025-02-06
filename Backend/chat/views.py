from django.shortcuts import render, redirect
from rest_framework import status

from Client.models import Client
from .models import Room, Message

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Message, Room
from .serializers import MessageSerializer


# Create your views here.
def get_client_ip_and_port(request):
    """
    Helper method to get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # If the request is forwarded, the IP is the first one in the list
        ip = x_forwarded_for.split(',')[0]
    else:
        # Otherwise, use the remote address
        ip = request.META.get('REMOTE_ADDR')
    return ip


def HomeView(request):
    if request.method == "POST":
        username = request.POST["username"]
        room = request.POST["room"]
        try:
            existing_room = Room.objects.get(room_name__icontains=room)
        except Room.DoesNotExist:
            r = Room.objects.create(room_name=room)
        return redirect("room", room_name=room, username=username)
    return render(request, "home.html")


# views.py (update RoomView)
def RoomView(request, room_name, username):
    existing_room = Room.objects.get(room_name__icontains=room_name)
    context = {
        "user": username,
        "room_name": existing_room.room_name,
    }
    return render(request, "room.html", context)


class MessageHistoryView(APIView):
    def get(self, request, room_name):
        room = Room.objects.get(room_name='main_room')
        messages = Message.objects.filter(room=room).order_by('created_at')
        serializer = MessageSerializer(messages, many=True,
                                       context={'request': request, "ip": get_client_ip_and_port(request), })
        return Response(serializer.data)


class UploadFileAPIView(APIView):
    def post(self, request, room_name):
        try:
            serializer = MessageSerializer(data=request.data)
            image_file = request.FILES.get('file', None)
            user_ip = get_client_ip_and_port(request)
            client = Client.objects.filter(ip__icontains=user_ip).first()
            if client is None:
                return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
            if serializer.is_valid():
                room = Room.objects.get(room_name__icontains=room_name, )
                msg = Message(**serializer.validated_data, room=room, file=image_file, sender=client)
                msg.save()
                return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # raise e
            return Response("Somrthing went wrong", status=status.HTTP_400_BAD_REQUEST)
