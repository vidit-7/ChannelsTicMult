from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
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

def against_comp(request):
    return render(request, 'game/board_computer.html')

def change_playername(request):
    if request.method == "POST":
        new_player_name = request.POST.get('player_name')
        if new_player_name:
            response = JsonResponse({
                'succes': True,
                'new_player_name': new_player_name
            })
            response.set_cookie(
                'player_name',
                str(new_player_name),
                max_age=60*60*24*7, #expiry
                httponly=False, # accessible by js
                samesite="Lax"
            )
        return JsonResponse({'success':False})