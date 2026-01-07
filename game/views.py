from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import GameRoom
import json, uuid, datetime

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

def create_room(request):
    if request.method=='POST':
        # # cleanup
        # GameRoom.objects.filter(expires_at__lt<datetime.now()).delete()

        game_code = f'room_{uuid.uuid4().hex[:8]}'

        room_obj = GameRoom.objects.create(
            room_code=game_code,
            expires_at = timezone.now() + datetime.timedelta(minutes=30)
        )

        return JsonResponse({'success': True, 'game_code': room_obj.room_code})


def game_board(request, room_code):
    if not request.COOKIES.get('temp_player_id'):
        return redirect('gameLobby')
    print(room_code)
    try:
        room_obj = GameRoom.objects.get(room_code=room_code)
        return render(request, 'game/board.html', {'room_code': room_code})
    except:
        print('room not found vw')
        return redirect('gameLobby')

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