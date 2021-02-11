from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.state import User


@database_sync_to_async
def get_user(validated_token):
    try:
        return JWTTokenUserAuthentication().get_user(validated_token=validated_token)
    except User.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query = dict((x.split("=") for x in scope["query_string"].decode().split("&")))
        validated_token = JWTTokenUserAuthentication().get_validated_token(
            raw_token=query.get("token")
        )
        scope["user"] = await get_user(validated_token=validated_token)
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))



'''
For Token Authentication
'''
# from django.contrib.auth.models import AnonymousUser
# from channels.db import database_sync_to_async
# from channels.middleware import BaseMiddleware
# from rest_framework.authtoken.models import Token

# @database_sync_to_async
# def get_user(token_key):
#     try:
#         token = Token.objects.get(key=token_key)
#         return token.user
#     except Token.DoesNotExist:
#         return AnonymousUser()

# class TokenAuthMiddleware(BaseMiddleware):

#     def __init__(self, inner):
#         self.inner = inner

#     async def __call__(self, scope, receive, send):
#         query = dict((x.split('=') for x in scope['query_string'].decode().split("&")))
#         token_key = query.get('token')
#         scope['user'] = await get_user(token_key)
#         return await super().__call__(scope, receive, send)