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
        player_id = cookies.get('temp_player_id')
        if not player_id:
            print("no player id")
            await self.close()
        print(f"player id {player_id} connected")
        if(self.room_name not in rooms_state):
            rooms_state[self.room_name] = {
                'players' : dict(), # {sessionid: {name: username}}
                'move_timer' : None,
                'room_timer' : time.time() + 1800, # half an hour
                'game_state' : game_logic.newGameBoard()
            }
        # assign users
        if(player_id not in rooms_state[self.room_name]['players']):
            if len(rooms_state[self.room_name]['players']) < 2:
                rooms_state[self.room_name]['players'][player_id] = {
                    'name': f"anon-{random.randint(1000,9999)}"
                }

                game_logic.assignSymbols(rooms_state[self.room_name]['game_state'], player_id)

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        

    async def disconnect(self, close_code):
        print(close_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        print(rooms_state)
        text_data_json = json.loads(text_data)
        message_action = text_data_json['action']
        message_data = text_data_json['message']

        cookies = self.scope['cookies']
        player_id = cookies.get('temp_player_id')

        current_game = rooms_state[self.room_name]['game_state']
        player_symbol = rooms_state[self.room_name]['game_state']['players'][player_id]


        if message_action == 'send_chat':
            await self.channel_layer.group_send(
                self.room_group_name, 
                {
                    'type': 'board_message',
                    # 'player_id' : player_id,
                    'message_data': message_data
                }
            )
        elif message_action == 'make_move':
            move_x = text_data_json['move_x']
            move_y = text_data_json['move_y']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_board_move',
                    # 'player_id': player_id,
                    'move_x': move_x,
                    'move_y': move_y,
                    'current_game': current_game,
                    'player_symbol': player_symbol
                }
            )
        # elif message_data == 'start_game':
        #     await self.channel_layer.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'ready_player',
        #             'player_id': player_id,
        #             'message_data': 'player ready'
        #         }
        #     )
    
    async def board_message(self, event):
        message = event['message_data']
        
        await self.send(
            text_data=json.dumps({
                'action': 'chat_message',
                'message_was': message
            })
        )

    async def player_board_move(self, event):
        move_x = event['move_x']
        move_y = event['move_y']
        player_id = event['player_id']
        player_symbol = event['player_symbol']
        current_game = event['current_game']
        moveMade = game_logic.playerMakeMove(current_game, move_x, move_y, player_id)

        # valid move
        if moveMade:
            send_valid_dict = {
                'action': 'player_moved',
                'success': True,
                'ch_x': move_x,
                'ch_y': move_y,
                'symbol': player_symbol
            }
            checkGame = game_logic.checkGameOverWin(current_game)
            # game not over
            if not checkGame[0]:
                send_valid_dict['game_over'] = False
            # game over
            else:
                send_valid_dict['game_over'] = True
                send_valid_dict['winner'] = checkGame[1]

            await self.send(
                text_data=json.dumps(send_valid_dict)
            )
        # invalid move
        else:
            await self.send(
                text_data=json.dumps({
                    'action': 'player_moved',
                    'success': False
                })
            )
    # async def ready_player(self, event):
    #     player_id = event['player_id']
    #     if len(rooms_state[self.room_name]['players']) == 0:
    #         rooms_state[self.room_name]['game_state']['players']['X'] = player_id
    #     elif len(rooms_state[self.room_name].players) == 1:
    #         rooms_state[self.room_name]['game_state']['players']['O'] = player_id

