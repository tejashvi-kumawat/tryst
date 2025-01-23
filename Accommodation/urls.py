from django.urls import path, include
from . import views

urlpatterns = [
    path('accomodation/', views.accommodation, name='accommodation'),
    path('verification/', views.verify_payment, name='verification'),
    path('cancel-order/', views.cancel_order, name='cancel-order')
]
