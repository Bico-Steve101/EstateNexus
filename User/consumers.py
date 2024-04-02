import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth import get_user_model
from .models import ChatMessage, Property

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_email = text_data_json.get('sender', '')
        receiver_email = text_data_json.get('receiver', '')
        await self.save_message(message, sender_email, receiver_email)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_email,
                'receiver': receiver_email
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_email = event.get('sender', '')
        receiver_email = event.get('receiver', '')
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender_email,
            'receiver': receiver_email
        }))

    @database_sync_to_async
    def save_message(self, message, sender_email, receiver_email):
        try:
            sender = User.objects.get(email=sender_email)
            if sender.role == 'tenant':
                receiver_email = sender.tenant.manager.user.email
                property = sender.tenant.property
            elif sender.role == 'manager':
                receiver_email = sender.manager.tenant.user.email
                property = sender.manager.property
            else:
                print(f"User with email {sender_email} is not a tenant or manager.")
                return

            receiver = User.objects.get(email=receiver_email)
            ChatMessage.objects.create(content=message, sender=sender,
                                       receiver=receiver, property=property,
                                       is_received=True)
        except User.DoesNotExist:
            print(f"User with email {sender_email} or {receiver_email} does not exist.")
        except Property.DoesNotExist:
            print("The specified property does not exist.")
