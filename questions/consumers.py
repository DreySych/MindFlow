import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SimpleDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "group"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_data(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'status': 'update',
            'data': message
        }))
