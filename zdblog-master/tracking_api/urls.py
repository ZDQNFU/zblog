from django.urls import path
from . import views

urlpatterns = [
    path('visitors/', views.VisitorListView.as_view(), name='tracking_visitor_list'),
    path('visitors/geo/', views.VisitorGeoView.as_view(), name='tracking_visitor_geo'),
    path('visitors/delete/', views.VisitorDeleteView.as_view(), name='tracking_visitor_delete'),
    path('visitors/<str:session_key>/', views.VisitorDetailView.as_view(), name='tracking_visitor_detail'),
]
