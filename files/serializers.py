from rest_framework import serializers

from profiles.serializers import ProfileSerializer
from .models import File, Share, ShareTime, Comment, ChatTime


class UploadFileSerializer(serializers.ModelSerializer):
    """File serializer"""

    user = ProfileSerializer(source="user.profile", read_only=True)

    class Meta:
        model = File
        fields = "__all__"


class FileListSerializer(serializers.ModelSerializer):
    """File list serializer"""

    class Meta:
        model = File
        fields = ('id', 'title', 'description', 'myfile')


class MyFileDetailSerializer(serializers.ModelSerializer):
    """My file detail serializer"""

    user = ProfileSerializer(source="user.profile", read_only=True)

    class Meta:
        model = File
        fields = "__all__"


class ReceivedFileDetailSerializer(serializers.ModelSerializer):
    """Received file detail serializer"""

    user = ProfileSerializer(source="user.profile", read_only=True)
    is_comment = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = File
        fields = "__all__"
    
    def get_is_comment(self, obj):
        share = Share.objects.get(user=self.context['request'].user)
        f_obj = ShareTime.objects.get(share=share, shared_file=obj)
        return f_obj.is_comment 


class ShareFileSerializer(serializers.Serializer):
    """File share serializer"""

    username = serializers.CharField(required=True)
    is_comment = serializers.BooleanField(default=False)

    def validate_username(self, value):
        value = value.lower().strip()
        return value


class ReceivedFileListSerializer(serializers.ModelSerializer):
    """Received files list serializer"""

    shared_file = FileListSerializer(read_only=True)
    sender = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ShareTime
        fields = ("shared_file", 'sender')

    def get_sender(self, obj):
        return obj.shared_file.user.username


class SentFileListSerializer(serializers.ModelSerializer):
    """Sent file list serializer"""

    receiver = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Share
        fields = ('receiver', 'timestamp')

    def get_receiver(self, obj):
        return obj.user.username


class SentFileDetailSerializer(serializers.ModelSerializer):
    """Sent file detail serializer"""

    shared_file = MyFileDetailSerializer(read_only=True)
    receiver = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ShareTime
        fields = ('shared_file', 'receiver', 'is_comment', 'timestamp')
    
    def get_receiver(self, obj):
        return obj.share.user.username


class CreateCommentSerializer(serializers.Serializer):
    """Create comment serializer"""

    content = serializers.CharField(required=True)
    username = serializers.CharField(required=True)


class UpdateCommentSerializer(serializers.Serializer):
    """Update comment serializer"""

    content = serializers.CharField(required=True)


class CommentUsernameSerializer(serializers.Serializer):
    """Get username serializer"""

    username = serializers.CharField(required=True)


class CommentSerializer(serializers.ModelSerializer):
    """Comments serializer"""

    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'username', 'content', 'timestamp')

    def get_username(self, obj):
        return obj.user.username


class ChatTimeSerializer(serializers.ModelSerializer):
    """Chat Comments serializer"""

    comments = CommentSerializer(read_only=True)

    class Meta:
        model = ChatTime
        fields = ('comments', 'timestamp')

