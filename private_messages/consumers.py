import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from users.models import User
from .models import Message


class PersonalMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]

        if not self.user.is_authenticated:
            await self.close()
            return

        ids = sorted([self.user.id, self.other_user_id])
        self.room_name = f"chat_{ids[0]}_{ids[1]}"

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = data["message"]

        message = await self.save_message(text)

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "send_message",
                "message": message.text,
                "sender": self.user.username,
                "sender_id": self.user.id,
                "time": message.created_at.strftime("%H:%M"),
            }
        )

    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "sender_id": event["sender_id"],
            "time": event["time"],
        }))

    @database_sync_to_async
    def save_message(self, text):
        receiver = User.objects.get(id=self.other_user_id)

        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            text=text
        )