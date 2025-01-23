from django.urls import path
from . import views

urlpatterns = [
    path('pronite/', views.pronite, name='pronite'),
    path('slot/', views.slot, name='slot'),
    path('pass/', views.passes, name='pass'),
    path('pass/<str:slotId>/', views.bookPasses, name='bookPasses'),
    path('entry/', views.entry, name='entry'),
    path('qr/', views.qr, name='qr'),
    path('login/', views.login, name='login'),
    path('passes/enter/', views.enterPasses, name='enterPasses'),
    path('passes/internal/', views.internalpass, name='internalPass'),
]
