from django.urls import path
from message.views.c_views import MessageListView, MessageCreateView, MessageLikeToggleView
from message.views.s_views import SMessageListCreateView, SMessageRetrieveUpdateDestroyView

urlpatterns = [
    # C端
    path('c/list/', MessageListView.as_view(), name='c_message_list'),
    path('c/create/', MessageCreateView.as_view(), name='c_message_create'),
    path('c/<str:pk>/like/', MessageLikeToggleView.as_view(), name='c_message_like'),

    # S端
    path('s/messages/', SMessageListCreateView.as_view(), name='s_message_list_create'),
    path('s/messages/<str:pk>/', SMessageRetrieveUpdateDestroyView.as_view(), name='s_message_detail'),
]
