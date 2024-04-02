from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from User import consumers

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter([
        path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    ]),
})
