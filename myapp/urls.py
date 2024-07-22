from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_name, name='get_name'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
]
