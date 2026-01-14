from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page_redir),
    path('game/against-comp/', views.against_comp, name="gameAgainstComp"),
    path('game/lobby/', views.game_lobby, name="gameLobby"),
    # path('game/js-change-player-name/', views.change_playername, name="changePlayerName"),
    path('game/create-room/', views.create_room, name="gameCreateRoom"),
    path('game/board/<str:room_code>/', views.game_board, name="gameBoard"),
]