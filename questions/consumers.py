import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SimpleDataConsumer(AsyncWebsocketConsumer):
    """WebSocket-потребитель для рассылки обновлений (вопросы, комментарии, ответы)."""

    async def connect(self):
        """Принимает соединение и добавляет канал в группу."""
        self.group_name = "group"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """При закрытии соединения удаляет канал из группы."""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_data(self, event):
        """Отправляет клиенту JSON с данными события (новый пост, комментарий, ответ)."""
        message = event['message']
        await self.send(text_data=json.dumps({
            'status': 'update',
            'data': message
        }))
