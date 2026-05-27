from django.urls import path
from .views.c_views import ResourceLinkListView
from .views.s_views import SResourceLinkListCreateView, SResourceLinkRetrieveUpdateDestroyView

urlpatterns = [
    # ================= C端（公开接口） =================
    path('c/links/', ResourceLinkListView.as_view(), name='c_link_list'),

    # ================= S端（管理接口） =================
    path('s/links/', SResourceLinkListCreateView.as_view(), name='s_link_list_create'),
    path('s/links/<str:pk>/', SResourceLinkRetrieveUpdateDestroyView.as_view(), name='s_link_detail'),
]
