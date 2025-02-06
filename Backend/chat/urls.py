# urls.py
from django.urls import path
from .views import HomeView, RoomView, MessageHistoryView, UploadFileAPIView

urlpatterns = [
    path("", HomeView, name="login"),
    path("<str:room_name>/<str:username>/", RoomView, name="room"),
    path("api/messages/<str:room_name>/file", UploadFileAPIView.as_view(), name="message-file"),
    path("api/messages/<str:room_name>/", MessageHistoryView.as_view(), name="message-history"),

]