from django.urls import path
from .views import BotView

urlpatterns = [
    path('2f45d78ae6454f8e8056fa2a56475f55d5b8a9fa5d0be59301/', BotView.as_view(), name='webhook')
]
