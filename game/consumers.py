import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class GameMoveConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'board_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(close_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_data = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                'type': 'board_message',
                'message_data': message_data
            }
        )
    
    async def board_message(self, event):
        message = event['message_data']
        
        await self.send(
            text_data=json.dumps({
                # 'type': 'message_received',
                'message_was': message
            })
        )

# no async version
# class GameMoveConsumer(WebsocketConsumer):
    
#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'board_{self.room_name}'

#         # join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
        
#         self.accept()

#         # self.send(text_data=json.dumps({
#         #     'type': 'connection_established',
#         #     'msg': 'is this called handshake?'
#         # }))

#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )
#         print(close_code)

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'board_message',
#                 'message': message
#             }
#         )

#         print(f"Message: {message}")

#         # self.send(text_data=json.dumps({
#         #     'type': 'message_received',
#         #     'message_was': message 
#         # }))
#     def board_message(self, event):
#         message = event['message']

#         self.send(text_data=json.dumps(
#             {
#                 'type': 'message_received',
#                 'message_was': message
#             }
#         ))