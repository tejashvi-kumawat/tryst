from django.urls import path
from . import views

urlpatterns = [
    path('', views.merchandise, name='merchandise'),
    path('confirm/', views.confirmMerchandise, name='confirmMerchandise'),
]