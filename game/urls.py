from django.urls import path
from . import views

urlpatterns = [
    path('against-comp/', views.against_comp, name="gameAgainstComp"),
    path('lobby/', views.game_lobby, name="gameLobby"),
    # path('js-change-player-name/', views.change_playername, name="changePlayerName"),
    path('create-room/', views.create_room, name="gameCreateRoom"),
    path('board/<str:room_code>/', views.game_board, name="gameBoard"),
]