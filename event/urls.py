from django.urls import path
from . import views

urlpatterns = [
    path('create_event/', views.create_event, name='create_event'),
    path('registration/', views.registration, name='registration'),
    path('create_workshop/', views.create_workshop, name='create_workshop'),
    path('create_guest/', views.create_guest, name='create_guest'),
    path('allevents/', views.get_all_events, name='allevents'),
    path('registered/', views.get_registered_events, name='registered'),
    path('register/', views.register, name='register'),
    path('check_registration/', views.check_registration,
         name='check_registration'),
]
