from django.urls import path
from . import views

urlpatterns = [
    path('lobby/', views.game_lobby, name="gameLobby"),
    path('js-change-player-name/', views.change_playername, name="changePlayerName"),
    path('board/<str:room_name>/', views.game_board, name="gameBoard"),
]