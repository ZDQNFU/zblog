from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .chat_views import (
    ChatStreamView,
    ChatHistoryView,
    ChatUserListView,
    ChatUserDetailView,
    ChatClearView,
    ChatTrimView,
)

urlpatterns = [
    path('captcha/', views.CaptchaView.as_view(), name='captcha'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.UserInfoView.as_view(), name='user_info'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    # 用户管理（仅超管）
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    # 注册
    path('send-code/', views.SendVerificationCodeView.as_view(), name='send_code'),
    path('register/', views.RegisterView.as_view(), name='register'),
    # 聊天（仅超管/staff）
    path('chat/', ChatStreamView.as_view(), name='chat_stream'),
    path('chat/history/', ChatHistoryView.as_view(), name='chat_history'),
    # 聊天管理（仅超管）
    path('chat/users/', ChatUserListView.as_view(), name='chat_user_list'),
    path('chat/users/<int:user_id>/', ChatUserDetailView.as_view(), name='chat_user_detail'),
    path('chat/users/<int:user_id>/clear/', ChatClearView.as_view(), name='chat_clear'),
    path('chat/users/<int:user_id>/trim/', ChatTrimView.as_view(), name='chat_trim'),
]
