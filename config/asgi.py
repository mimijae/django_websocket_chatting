"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

# channels에서 필요한 미들웨어와 라우팅 객체를 가져옵니다.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
# Django의 기본 ASGI 어플리케이션 객체를 가져옵니다. (사실 여기서는 이제 사용되지 않음)
from django.core.asgi import get_asgi_application

# Django의 기본 설정 모듈을 지정합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# chat 앱의 라우팅 설정을 가져옵니다.
import chat.routing  # noqa: E402

# 전체 ASGI 어플리케이션 구성을 정의합니다.
application = ProtocolTypeRouter({
    # 웹소켓 요청은 AllowedHostsOriginValidator로 유효성을 검사한 후,
    # AuthMiddlewareStack을 거쳐 URLRouter로 라우팅됩니다.
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        )
    ),
})
