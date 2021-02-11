from django.urls import path, re_path

from .views import *


urlpatterns = [
    path('upload-file/', UploadFileView.as_view(), name='upload-file'),
    path('share-file/<int:file_id>/', ShareFileView.as_view(), name='share-file'),

    path('my-files/', FileListView.as_view(), name='my-files'),
    path('my-file/<int:pk>/', MyFileDetailView.as_view(), name='my-file-detail'),
    path('my-file/<int:file_id>/sents/', SentFileListView.as_view(), name='sent-file-list'),

    path('my-file/<int:file_id>/sent/<str:username>/', \
        SentFileDetailView.as_view(), name='sent-file-detail'),

    path('received-files/', ReceivedFileListView.as_view(), name='receiving-files'),
    path('received-file/<int:pk>/', ReceivedFileDetailView.as_view(), name='received-file-detail'),
    
    path('shared-file/<int:file_id>/create-comment/', \
        CreateCommentView.as_view(), name='create-comment'),

    path('shared-file/<int:file_id>/comments/', \
        FileCommentListView.as_view(), name='comments'),
    
    path('shared-file/<int:file_id>/comment/<int:com_id>/delete/', \
        RemoveCommentView.as_view(), name='delete-comment'),
    
    path('shared-file/<int:file_id>/comment/<int:com_id>/update/', \
        EditCommentView.as_view(), name='edit-comment'),
]
