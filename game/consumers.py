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

        if not self.player_id:
            print("no player id")
            await self.close()
        print(f"player id {self.player_id} connected")
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
                rooms_state[self.room_name]['players'][self.player_id] = {
                    'name': f"anon-{random.randint(1000,9999)}"
                }

                game_logic.assignSymbols(rooms_state[self.room_name]['game_state'], self.player_id)

        if self.player_id in rooms_state[self.room_name]['players']:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        

    async def disconnect(self, close_code):
        print(close_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        # print(rooms_state)
        text_data_json = json.loads(text_data)
        message_action = text_data_json['action']

        # current_game_state = rooms_state[self.room_name]['game_state']
        # player_symbol = rooms_state[self.room_name]['game_state']['players'][player_id]


        if message_action == 'send_chat':
            message_data = text_data_json['message_body']
            await self.channel_layer.group_send(
                self.room_group_name, 
                {
                    'type': 'board_message',
                    'player_id': self.player_id,
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
                    'player_id': self.player_id,
                    'move_x': move_x,
                    'move_y': move_y,
                }
            )
    
    async def board_message(self, event):
        message = event['message_data']
        # store the player's id to send as payload
        sender_player_id = event['player_id']
        room = rooms_state[self.room_name]
        room['chat_log'].append((sender_player_id, message))

        print(room['chat_log'])

        await self.send(
            text_data=json.dumps({
                'action': 'chat_message',
                'player_id': sender_player_id,
                'message_was': message
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
        except:
            print("invalid move index")
            return
        

        send_dict = dict()
        # only attempt to make the move if the sending player (self.player_id from connection)
        # is the expected move maker
        moveMade = False
        expectedPlayer = False
        gameOver = (False, None)
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
        # # valid move
        # if moveMade:
        #     send_dict = {
        #         'action': 'player_moved',
        #         'success': True,
        #         'ch_x': move_x,
        #         'ch_y': move_y,
        #         'symbol': player_symbol
        #     }
        #     checkGame = game_logic.checkGameOverWin(current_game_state)
        #     # game not over
        #     if not checkGame[0]:
        #         send_dict['game_over'] = False
        #     # game over
        #     else:
        #         send_dict['game_over'] = True
        #         send_dict['winner'] = checkGame[1]
    
        # # only need to send the data to the player attempting the invalid move
        # else:
        #     send_dict = {
        #         'action': 'player_moved',
        #         'success': False
        #     }
        #     if expectedPlayer:
        #         send_dict['fail_message'] = 'Invalid Move'
        #     else:
        #         send_dict['fail_message'] = 'Invalid Turn'

        # send the data to everyone
        await self.send(
            text_data=json.dumps(send_dict)
        )

