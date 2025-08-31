from django.shortcuts import render

# Create your views here.

def game_lobby(request):
    return render(request, 'game/lobby.html')

def game_board(request, room_name):
    return render(request, 'game/board.html', {'room_name': room_name})