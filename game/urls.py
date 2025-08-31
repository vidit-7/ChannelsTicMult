from django.urls import path
from . import views

urlpatterns = [
    path('lobby/', views.game_lobby, name="gameLobby"),
    path('board/<str:room_name>/', views.game_board, name="gameBoard"),
]