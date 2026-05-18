from django.urls import path

from .views import (
    ChatStreamView,
    ChatHistoryView,
    ChatUserListView,
    ChatUserDetailView,
    ChatClearView,
    ChatTrimView,
)

urlpatterns = [
    path('stream/', ChatStreamView.as_view(), name='chat_stream'),
    path('history/', ChatHistoryView.as_view(), name='chat_history'),
    path('users/', ChatUserListView.as_view(), name='chat_user_list'),
    path('users/<int:user_id>/', ChatUserDetailView.as_view(), name='chat_user_detail'),
    path('users/<int:user_id>/clear/', ChatClearView.as_view(), name='chat_clear'),
    path('users/<int:user_id>/trim/', ChatTrimView.as_view(), name='chat_trim'),
]
