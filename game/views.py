from django.shortcuts import render, redirect
import uuid

# Create your views here.

def game_lobby(request):
    response = render(request, 'game/lobby.html')

    if not request.COOKIES.get('temp_player_id'):
        response.set_cookie(
            'temp_player_id', # key
            str(uuid.uuid4()), # value
            max_age=60*60*24*2, #expiry
            httponly=True, # inaccessible by js
            samesite="Lax"
        )    
    return response

def game_board(request, room_name):
    if not request.COOKIES.get('temp_player_id'):
        return redirect('gameLobby')

    return render(request, 'game/board.html', {'room_name': room_name})