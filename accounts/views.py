from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from django.conf import settings

from .models import User
from .serializers import UsernameSerializer, EmailSerializer


class CheckUsernameView(APIView):
    """Checking username already exist or not"""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UsernameSerializer,
        responses={200: 'Boolean True or False'}
    )
    def post(self, request):
        serializer = UsernameSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            username = data.get("username")
            if User.objects.filter(username=username).exists():
                return Response({"username_is_exist": True}, status=200)
            else:
                return Response({"username_is_exist": False}, status=200)


class CheckEmailView(APIView):
    """Checking email already exist or not"""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=EmailSerializer,
        responses={200: 'Boolean True or False'}
    )
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            email = data.get("email")
            if User.objects.filter(email=email).exists():
                return Response({"email_is_exist": True}, status=200)
            else:
                return Response({"email_is_exist": False}, status=200)
