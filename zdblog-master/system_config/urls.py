from django.urls import path

from system_config.views.s_views import (
    SSystemConfigListCreateView,
    SSystemConfigRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('s/configs/', SSystemConfigListCreateView.as_view(), name='s_config_list_create'),
    path('s/configs/<int:pk>/', SSystemConfigRetrieveUpdateDestroyView.as_view(), name='s_config_detail'),
]
