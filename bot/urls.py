
from django.urls import path
from .views import index, ChatAPIView

urlpatterns = [
    path("", index, name="index"),
    path("api/chat/", ChatAPIView.as_view(), name="bot_api"),
]
