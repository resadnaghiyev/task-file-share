from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from django.conf import settings
from django.db.models import Q
from itertools import chain
from operator import attrgetter

from accounts.models import User
from .models import File, Share, ShareTime, Comment, Chat, ChatTime
from .serializers import (
    UploadFileSerializer, 
    FileListSerializer, 
    MyFileDetailSerializer,
    ShareFileSerializer,
    SentFileListSerializer,
    SentFileDetailSerializer,
    ReceivedFileListSerializer, 
    ReceivedFileDetailSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    UpdateCommentSerializer, 
    CommentUsernameSerializer,
    ChatTimeSerializer
)


class UploadFileView(generics.CreateAPIView):
    """Fayl yükləmək"""

    permission_classes = [IsAuthenticated]
    serializer_class = UploadFileSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            return None
        serializer.save(user=self.request.user)


class FileListView(generics.ListAPIView):
    """Yüklədiyim faylların siyahısı"""

    permission_classes = [IsAuthenticated]
    serializer_class = FileListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return File.objects.none()

        return File.objects.filter(user=self.request.user)


class MyFileDetailView(generics.RetrieveAPIView):
    """Faylın detallı təsviri"""

    permission_classes = [IsAuthenticated]
    serializer_class = MyFileDetailSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return File.objects.none()

        qs = File.objects.filter(
            Q(user=self.request.user) | \
            Q(shared__user=self.request.user)
        ).distinct()
        return qs
    

class ShareFileView(APIView):
    """Faylı paylaşmaq"""

    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        serializer = ShareFileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get('username')
            is_comment = serializer.validated_data.get('is_comment')
            file_obj = get_object_or_404(File, pk=file_id, user=request.user)
            user = get_object_or_404(User, username=username)
            share_list, created = Share.objects.get_or_create(user=user)
            if Share.objects.filter(user=user, shared_file=file_id).exists():
                return Response(
                    {"message": "You already shared this file"}, status=200
                )
            else:
                share_list.shared_file.add(file_obj)
                if is_comment:
                    obj = ShareTime.objects.filter(
                        share=share_list, shared_file=file_obj
                    ).update(is_comment=True)
                    chat = Chat.objects.create(file=file_obj)
                    chat.participants.add(user, request.user)
                return Response(
                    {"message": "Successfully shared"}, status=200
                )


class ReceivedFileListView(generics.ListAPIView):
    """Qəbul olunmuş faylların siyahısı"""

    permission_classes = [IsAuthenticated]
    serializer_class = ReceivedFileListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Share.objects.none()

        obj = Share.objects.filter(user=self.request.user)
        return ShareTime.objects.filter(share=obj.first())


class ReceivedFileDetailView(generics.RetrieveAPIView):
    """Qəbul olunmuş faylın detallı təsviri"""

    permission_classes = [IsAuthenticated]
    serializer_class = ReceivedFileDetailSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return File.objects.none()

        qs = File.objects.filter(
            Q(user=self.request.user) | \
            Q(shared__user=self.request.user)
        ).distinct()
        return qs


class SentFileListView(APIView):
    """Göndərilmiş faylların siyahısı"""

    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        file_obj = File.objects\
            .filter(user=request.user, id=file_id).first()
        if file_obj:
            qs = file_obj.shared.all()
            serializer = SentFileListSerializer(qs, many=True)
            return Response(serializer.data, status=200)
        else:
            return Response({'not found'}, status=404)


class SentFileDetailView(APIView):
    """Göndərilmiş faylların siyahısı"""

    permission_classes = [IsAuthenticated]

    def get(self, request, file_id, username):
        file_obj = File.objects.filter(
            user=request.user, id=file_id
        ).first()
        user = get_object_or_404(User, username=username)
        if file_obj:  
            obj = Share.objects.filter(user=user).first()
            s_obj = ShareTime.objects.filter(share=obj).first()
            serializer = SentFileDetailSerializer(s_obj)
            return Response(serializer.data, status=200)
        else:
            return Response({'not found'}, status=404)


class CreateCommentView(APIView):
    """Fayl üçün şərh yazmaq"""

    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        file_obj = get_object_or_404(File, id=file_id)
        serializer = CreateCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            content = serializer.validated_data.get("content")
            username = serializer.validated_data.get("username")
            user = get_object_or_404(User, username=username)
            chat = Chat.objects.filter(
                file=file_obj, participants=user
            ).filter(participants=request.user).first()
            if chat:
                new_comment = Comment.objects.create(
                    user=request.user,
                    content=content,
                )
                chat.comments.add(new_comment)
                serializer = CommentSerializer(new_comment)
                return Response(serializer.data, status=201)
            else:
                return Response({'Not found'}, status=404)


class FileCommentListView(APIView):
    """Fayl üçün yazılmış şərhlər"""

    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        file_obj = get_object_or_404(File, id=file_id)
        serializer = CommentUsernameSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get("username")
            user = get_object_or_404(User, username=username)
            chat = Chat.objects.filter(
                file=file_obj, participants=user
            ).filter(participants=request.user).first()
            if chat:
                qs = ChatTime.objects.filter(chat=chat) \
                    .order_by('-timestamp')
                serializer = ChatTimeSerializer(qs, many=True)
                return Response(serializer.data, status=200)
            else:
                return Response({'Not found'}, status=404)


class RemoveCommentView(APIView):
    """Fayl üçün yazılmış şərhi silmək"""

    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id, com_id):
        file_obj = get_object_or_404(File, id=file_id)
        comment = get_object_or_404(Comment, id=com_id)
        chat = Chat.objects.filter(
            file=file_obj, participants=request.user
        ).filter(comments=comment).first()
        if (request.user == file_obj.user and chat) or \
            (request.user == comment.user and chat):
            comment.delete()
            return Response({'Successfully deleted'}, status=204)
        else:
            return Response({'Bad request'}, status=400)


class EditCommentView(APIView):
    """Fayl üçün yazılmış şərhi edit etmek"""

    permission_classes = [IsAuthenticated]        

    def post(self, request, file_id, com_id):
        file_obj = get_object_or_404(File, id=file_id)
        comment = get_object_or_404(Comment, id=com_id)
        chat = Chat.objects.filter(
            file=file_obj, participants=self.request.user
        ).filter(comments=comment).first()
        serializer = UpdateCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            content = serializer.validated_data.get('content')
        if request.user == comment.user and chat:
            Comment.objects.filter(id=com_id).update(content=content)
            return Response({'Successully updated'}, status=200)
        else:
            return Response({'Not found'}, status=404)
        