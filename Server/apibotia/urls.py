from django.contrib import admin
from django.urls import path, include
from .views import UserCreateAPIView, ObtainTokenAPIView, getScripts, getAllScripts, SendMessageAPIView

urlpatterns = [
    path('create-user/', UserCreateAPIView.as_view(), name='create_user'),
    path('get-token/', ObtainTokenAPIView.as_view(), name='get_token'),
    path('get-scripts/', getScripts.as_view(), name='get_scripts'),
    path('get-all-scripts/', getAllScripts.as_view(), name='get_all_scripts'),
    path('send-message/', SendMessageAPIView.as_view(), name='send_message'),
]