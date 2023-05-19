from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .global_registry import websockets

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        websockets[self.session_id] = self
        await self.accept()

    async def disconnect(self, close_code):
        del websockets[self.session_id]

    async def receive(self, text_data):
        pass  # handle received messages if necessary

    async def send_token(self, event):
        token = event['token']
        await self.send(text_data=json.dumps({
            'token': token,
        }))