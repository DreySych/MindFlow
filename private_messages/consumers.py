import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from notifications.models import create_notification
from users.models import User
from .models import Message


class PersonalMessageConsumer(AsyncWebsocketConsumer):
    """WebSocket-consumer для личного чата."""

    async def connect(self):
        self.user = self.scope['user']
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']

        if not self.user.is_authenticated or not self.user.active:
            await self.close()
            return

        self.room_name = self.get_room_name()
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )

    async def receive(self, text_data):
        if not self.user.is_authenticated or not self.user.active:
            return

        text = self.get_message_text(text_data)
        if not text:
            return

        message = await self.save_message(text)
        if not message:
            return

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'send_message',
                'message': message.text,
                'sender': self.user.username,
                'sender_id': self.user.id,
                'time': message.created_at.strftime('%H:%M'),
            }
        )

    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'time': event['time'],
        }))

    def get_room_name(self):
        """Создаёт одинаковое имя комнаты для двух пользователей."""
        user_ids = sorted([int(self.user.id), int(self.other_user_id)])
        return f'chat_{user_ids[0]}_{user_ids[1]}'

    @staticmethod
    def get_message_text(text_data):
        """Достаёт текст сообщения из JSON."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return ''

        return data.get('message', '').strip()

    @database_sync_to_async
    def save_message(self, text):
        """Сохраняет сообщение и создаёт уведомление получателю."""
        try:
            receiver = User.objects.get(id=self.other_user_id)
        except User.DoesNotExist:
            return None

        message = Message.objects.create(
            sender=self.user,
            receiver=receiver,
            text=text
        )
        create_notification(
            user=receiver,
            text=f'{self.user.username} написал вам сообщение',
            link=f'/profile/{self.user.username}/?open_chat={self.user.id}&chat_username={self.user.username}'
        )
        return message
