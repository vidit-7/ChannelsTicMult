import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import time
from . import game_logic
# import uuid
import math
import random

rooms_state = dict() # key room_group_name or room_name : 

class GameMoveConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
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
                'players' : dict(),
                'chat_log': list(), # {sessionid: {name: username}}
                'move_timer' : None,
                'room_timer' : time.time() + 1800, # half an hour
                'game_state' : game_logic.newGameState()
            }
        # assign users
        if len(rooms_state[self.room_name]['players']) < 2:
            if(self.player_id not in rooms_state[self.room_name]['players']):
                assignPlayerNames(rooms_state[self.room_name], self.player_id, self.player_name)
                game_logic.assignSymbols(rooms_state[self.room_name]['game_state'], self.player_id)

        if self.player_id in rooms_state[self.room_name]['players']:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            room = rooms_state[self.room_name]
            await self.send(text_data=json.dumps({
                'action': 'connection_made',
                # 'players': room['players'].values(),
                'chat_log': room['chat_log'],
                'board_state': room['game_state']['board'],
                'winner': room['game_state']['winner']
            }))
        

    async def disconnect(self, close_code):
        print(close_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
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
            
            await self.channel_layer.group_send(
                self.room_group_name, 
                {
                    'type': 'board_message',
                    'player_id': self.player_id,
                    'player_name': sender_player_name,
                    'message_data': message_data
                }
            )
        elif message_action == 'make_move':
            # only let the board work if 2 players have joined
            if len(room['players']) < 2:
                return
            move_x = text_data_json['move_x']
            move_y = text_data_json['move_y']
    
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_board_move',
                    'player_id': self.player_id,
                    'player_name': sender_player_name,
                    'move_x': move_x,
                    'move_y': move_y,
                }
            )
    
    async def board_message(self, event):
        message = event['message_data']
        message_data_clean = message.strip()
        if not message_data_clean:
            return
        # store the player's id to send as payload
        sender_player_id = event['player_id']
        sender_player_name = event['player_name']
        room = rooms_state[self.room_name]
        room['chat_log'].append((sender_player_name, message))

        print(room['chat_log'])

        await self.send(
            text_data=json.dumps({
                'action': 'chat_message',
                # 'player_id': sender_player_id,
                'player_name': sender_player_name,
                'message_was': message_data_clean
            })
        )

    async def player_board_move(self, event):
        
        move_x = event['move_x']
        move_y = event['move_y']
        sender_player_id = event['player_id']

        room = rooms_state[self.room_name]

        print(room['game_state'])
        # cookies = self.scope['cookies']
        # player_id = cookies.get('temp_player_id')
        current_game_state = room['game_state']
        expected_player_id = current_game_state['symbol_to_pid'][current_game_state['turn']]
        # player_symbol = current_game_state['pid_to_symbol'][expected_player_id]

        try:
            x, y = int(move_x), int(move_y)
            if not (0<=x<=2 and 0<=y<=2):
                return
        except:
            print("invalid move index")
            return
        
        send_dict = dict()
        moveMade = False
        expectedPlayer = False
        gameOver = (False, None)

        # only attempt to make the move if the sending player (self.player_id from connection)
        # is the expected move maker
        if sender_player_id == expected_player_id:
            expectedPlayer = True
            moveMade = game_logic.playerMakeMove(current_game_state, x, y, sender_player_id)

        gameOver = game_logic.checkGameOverWin(current_game_state)
        send_dict = {
            'action': 'player_moved',
            'expected_player': expectedPlayer,
            'success': moveMade,
            'board' : current_game_state['board'],
            'game_over': gameOver[0],
            'winner' : gameOver[1]
        }

        # send the data to everyone
        await self.send(
            text_data=json.dumps(send_dict)
        )

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

# def assignPlayersReadyState(room, player_id):
#     pass