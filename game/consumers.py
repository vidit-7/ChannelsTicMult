import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import time
import asyncio
from . import game_logic
from .models import GameRoom
# import uuid
import math
import random

rooms_state = dict() # key room_group_name or room_name : 

class GameMoveConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        temp_room_name = self.scope['url_route']['kwargs']['room_name']
        if(check_room_code_exists(temp_room_name) == None):
            print('room does not exist')
            await self.close()
        self.room_name = temp_room_name
        self.room_group_name = f'board_{self.room_name}'

        cookies = self.scope['cookies']
        self.player_id = cookies.get('temp_player_id')
        self.player_name = cookies.get('player_name')

        if not self.player_id:
            print("no player id")
            await self.close()

        print(f"player {self.player_name}:{self.player_id} connected")
        if(self.room_name not in rooms_state):
            rooms_state[self.room_name] = {
                'players' : dict(), # {sessionid: {name: username, reset_wish = }}
                'chat_log': list(), 
                'move_timer_task' : None,
                'next_move_time_limit' : None,
                # 'room_timer' : time.time() + 1800, # half an hour
                'game_state' : game_logic.newGameState(),
                'symbol_to_pid': dict(),
                'pid_to_symbol': dict(),
                'symbol_to_pname': dict(),
                'winner_log': list()
            }
        # assign users
        if len(rooms_state[self.room_name]['players']) < 2:
            if(self.player_id not in rooms_state[self.room_name]['players']):
                assignPlayerNames(rooms_state[self.room_name], self.player_id, self.player_name)
                rooms_state[self.room_name]['players'][self.player_id]['reset_wish'] = False
                assignSymbols(rooms_state[self.room_name], self.player_id)

        if self.player_id in rooms_state[self.room_name]['players']:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            room = rooms_state[self.room_name]
            # player_names = set()
            # for player_info in room['players'].value():
            #     player_names.add(player_info['name'])
            player_joined = room['players'][self.player_id]['name']
            player_ready = room['players'][self.player_id]['reset_wish']
            await self.send(text_data=json.dumps({
                'action': 'connection_made',
                'player_name': player_joined,
                'player_ready': player_ready,
                'chat_log': room['chat_log'],
                'board_state': room['game_state']['board'],
                'winner': room['game_state']['winner']
            }))

            rooms_state[self.room_name]['chat_log'].append(('game_sys', f'{player_joined} joined'))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_joined_room',
                    'player_name': player_joined,
                    'player_symbols': room['symbol_to_pname'],
                    'turn': room['game_state']['turn'],
                    'next_move_time_limit': room['next_move_time_limit']
                }
            )
        

    async def disconnect(self, close_code):
        print(close_code)
        player_left = rooms_state[self.room_name]['players'][self.player_id]['name']
        rooms_state[self.room_name]['chat_log'].append(('game_sys', f'{player_left} left'))
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_left_room',
                'player_name': player_left,
                'player_symbols': rooms_state[self.room_name]['symbol_to_pname']
            }
        )
    
    async def receive(self, text_data):
        # print(rooms_state)
        text_data_json = json.loads(text_data)
        message_action = text_data_json['action']
        room = rooms_state[self.room_name]
        sender_player_name = room['players'][self.player_id]['name']
        # current_game_state = rooms_state[self.room_name]['game_state']
        # player_symbol = rooms_state[self.room_name]['game_state']['players'][player_id]


        if message_action == 'send_chat':
            message_data = text_data_json['message_body']
            message_data_clean = message_data.strip()
            if not message_data_clean:
                return

            room = rooms_state[self.room_name]
            room['chat_log'].append((sender_player_name, message_data_clean))

            print(room['chat_log'])
            
            await self.channel_layer.group_send(
                self.room_group_name, 
                {
                    'type': 'board_message',
                    'player_id': self.player_id,
                    'player_name': sender_player_name,
                    'message_data': message_data_clean
                }
            )
        elif message_action == 'make_move':
            # player_ready = room['players'][self.player_id]['reset_wish']
            
            move_x = text_data_json['move_x']
            move_y = text_data_json['move_y']
            game_state = room['game_state']
            
            if len(room['players']) < 2:
                await self.send(text_data=json.dumps({
                    'action': 'move_failed',
                    'fail_msg': 'Wait for your opponent to join'
                })) 
                return
            if game_state['winner']!=None:
                print("game is over")
                await self.send(text_data=json.dumps({
                    'action': 'move_failed',
                    'fail_msg': 'Game is over'
                })) 
                return
            
            expected_player_id = room['symbol_to_pid'][game_state['turn']]
            playerSymbol = room['pid_to_symbol'][self.player_id]

            if self.player_id != expected_player_id:
                print("Not your turn")
                await self.send(text_data=json.dumps({
                    'action': 'move_failed',
                    'fail_msg': 'Not your turn'
                })) 
                return

            if not isValidMove(move_x, move_y):
                print("invalid move index")
                # await self.send(text_data=json.dumps({
                #     'action': 'move_failed',
                #     'fail_msg': 'Invalid move'
                # })) 
                return

            moveMade = game_logic.playerMakeMove(game_state, int(move_x), int(move_y), playerSymbol)

            winner_name = None
            winner_msg = ""
            game_over = False
            if moveMade:
                # start new timer for the other player on successful move
                if room['move_timer_task'] != None and not room['move_timer_task'].done():
                    room['move_timer_task'].cancel()
                    room['next_move_time_limit'] = None
                # create the timer task after checking if the game is over

                # check if game is over
                updated_game_state = room['game_state']
                gameOver = game_logic.checkGameOverWin(updated_game_state)

                # # timer created after setting winner details
                # room['move_timer_task'] = asyncio.create_task(self.move_timer_coroutine())

                game_over = gameOver[0]
                if gameOver[0]:
                    print(room)
                    if gameOver[1] != "Tie":
                        winner_id = room['symbol_to_pid'][gameOver[1]]
                        winner_name = room['players'][winner_id]['name']
                    else:
                        winner_name = "Tie"
                    winner_msg = f"{winner_name} {playerSymbol if winner_name!='Tie' else ''}"
                    room['winner_log'].append(winner_name)
                # only start new timer if game is not over
                else:
                    room['move_timer_task'] = asyncio.create_task(self.move_timer_coroutine())
                    room['next_move_time_limit'] = round((time.time() + 10) * 1000)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_board_move',
                        'player_name': sender_player_name,
                        'updated_game_state': updated_game_state,
                        'turn': room['game_state']['turn'],
                        'game_over': game_over,
                        'winner': winner_msg,
                        'next_move_time_limit' : room['next_move_time_limit']
                        # 'player_id': self.player_id,
                        # 'move_x': int(move_x),
                        # 'move_y': int(move_y),
                    }
                )
            else:
                print("move is not valid")
                self.send(json.dumps({
                    'action': 'move_failed',
                    'fail_msg': 'Invalid move'
                })) 

        elif message_action == 'reset_game':
            play_again_value = text_data_json['play_again_value']
            try:
                play_again_value = bool(play_again_value)
            except:
                print("invalid reset req")
                return
            
            room = rooms_state[self.room_name]
            player = room['players'][self.player_id]
            player_name = player['name']
            player['reset_wish'] = play_again_value

            reset_msg_disp = f"{player_name} wants to {'reset' if play_again_value else 'cancel reset'}"
            print("reset", room)

            if bothReadyToReset(room['players']):
                reset_msg_disp += "\nGame has been reset"
                print("reset", room['players'])
                for player_info in room['players'].values():
                    player_info['reset_wish'] = False
                room['game_state'] = game_logic.newGameState()

                # reset timer details
                if room['move_timer_task'] !=None:
                    room['move_timer_task'].cancel()
                    room['move_timer_task'] = None
                room['next_move_time_limit'] = None

                fresh_game_state = room['game_state']
                print("reset", fresh_game_state)
                board = fresh_game_state['board']
                winner = fresh_game_state['winner']

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'play_again_reset',
                        'reset_state': True,
                        'reset_message': reset_msg_disp,
                        'turn': fresh_game_state['turn'],
                        'next_move_time_limit': room['next_move_time_limit'],
                        'board': board,
                        'winner': winner
                    }
                )
                
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'play_again_reset',
                        'reset_state': False,
                        'reset_message': reset_msg_disp
                    }
                )

            # set_play_again = assignPlayersReadyState(room, self.player_id, play_again_value)
            rooms_state[self.room_name]['chat_log'].append(('game_sys', reset_msg_disp))
    
    async def board_message(self, event):
        message_data = event['message_data']
        # store the player's id to send as payload
        sender_player_id = event['player_id']
        sender_player_name = event['player_name']

        await self.send(
            text_data=json.dumps({
                'action': 'chat_message',
                # 'player_id': sender_player_id,
                'player_name': sender_player_name,
                'message_was': message_data
            })
        )

    async def player_board_move(self, event):
        updated_game_state = event['updated_game_state']
        move_maker_name = event['player_name']
        game_over = event['game_over']
        winner = event['winner']
        turn = event['turn']
        next_move_time_limit = event['next_move_time_limit']

        print(updated_game_state)

        send_dict = {
            'action': 'player_moved',
            # 'expected_player': expectedPlayer,
            'board' : updated_game_state['board'],
            'turn': turn,
            'next_move_time_limit': next_move_time_limit,
            'game_over':  game_over,
            'winner' : winner
        }

        # send the data to everyone
        await self.send(
            text_data=json.dumps(send_dict)
        )

    # called on each move
    async def move_timer_coroutine(self):
        if rooms_state[self.room_name]['game_state']['winner'] != None:
            return
        await asyncio.sleep(10)
        room = rooms_state[self.room_name]
        game_state = room['game_state']
        turn = game_state['turn']
        winner_symbol = "X" if turn != "X" else "O"
        winner_pid = room['symbol_to_pid'][winner_symbol]
        winner_name = room['players'][winner_pid]['name']
        game_state['winner'] = winner_symbol
        room['winner_log'].append(f"{winner_name}_on_time")
        winner_msg = f"{winner_name} {winner_symbol} won on time"

        print(f"timer over {winner_msg}")
        # # set timer to none now that the game is over
        # # not necessary maybe since it is done in game reset too
        # room['move_timer_task'] = None

        await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'timer_over',
                    'updated_game_state': game_state,
                    'game_over': True,
                    'winner': winner_msg,
                }
            )
    
    async def timer_over(self, event):
        game_state = event['updated_game_state']
        game_over = event['game_over']
        winner_msg = event['winner']

        send_dict = {
            'action': 'move_timer_over',
            # 'expected_player': expectedPlayer,
            'board' : game_state['board'],
            'game_over':  game_over,
            'winner' : winner_msg
        }

        await self.send(
            text_data = json.dumps(send_dict)
        )

    async def play_again_reset(self, event):
        reset_state = event['reset_state']
        reset_message = event['reset_message']
        send_dict = {
            'action': 'game_reset',
            'reset_state' : reset_state,
            'reset_message': reset_message 
        }
        if reset_state:
            fresh_board = event['board']
            winner = event['winner']
            send_dict['board'] = fresh_board
            send_dict['winner'] = winner
            send_dict['turn'] = event['turn']
            send_dict['next_move_time_limit'] = event['next_move_time_limit']
        
        await self.send(json.dumps(send_dict))
        
        
    async def player_joined_room(self, event):
        player_name = event['player_name']
        player_symbols = event['player_symbols']
        turn = event['turn']
        next_move_time_limit = event['next_move_time_limit']
        await self.send(json.dumps({
            'action': 'player_joined',
            'player_name': player_name,
            'player_symbols' : player_symbols,
            'turn': turn,
            'next_move_time_limit': next_move_time_limit
        }))

    async def player_left_room(self, event):
        player_name = event['player_name']
        player_symbols = event['player_symbols']
        await self.send(json.dumps({
            'action': 'player_left',
            'player_name': player_name,
            'player_symbols' : player_symbols
        }))


def assignPlayerNames(room, player_id, base_player_name):
    if not base_player_name:
        base_player_name = 'player'
    player_name = f"{base_player_name}#{random.randint(1000,9999)}"
    existing_names = set()
    for info_dict in room['players'].values():
        existing_names.add(info_dict['name'])
    
    while player_name in existing_names:
        player_name = f"{base_player_name}#{random.randint(1000,9999)}"
        
    room['players'][player_id] = {
        'name': player_name
    }

def isValidMove(move_x, move_y):
    try:
        x, y = int(move_x), int(move_y)
        if not (0<=x<=2 and 0<=y<=2):
            return False
    except:
        print("invalid move index")
        return False
    return True
        
def bothReadyToReset(players):
    reset_count = 0
    for player_info in players.values():
        if player_info['reset_wish'] == True:
            reset_count+=1
    if reset_count==2:
        return True
    return False
        
def assignSymbols(room, player_id):
    pname = room['players'][player_id]['name']
    if len(room['pid_to_symbol']) == 0:
        room['pid_to_symbol'][player_id] = "X"
        room['symbol_to_pid']["X"] = player_id
        room['symbol_to_pname']["X"] = pname
    elif len(room['pid_to_symbol']) == 1:
        room['pid_to_symbol'][player_id] = "O"
        room['symbol_to_pid']["O"] = player_id
        room['symbol_to_pname']["O"] = pname
    
def removeSymbols(room, player_id):
    if len(room['pid_to_symbol']) == 0:
        room['pid_to_symbol'][player_id] = None
        room['symbol_to_pid']["X"] = None
    elif len(room['pid_to_symbol']) == 1:
        room['pid_to_symbol'][player_id] = None
        room['symbol_to_pid']["O"] = None


@database_sync_to_async
def check_room_code_exists(room_code):
    room_obj = None
    try:
        room_obj = GameRoom.objects.get(room_code=room_code)
    except:
        room_obj = None
    
    return room_obj