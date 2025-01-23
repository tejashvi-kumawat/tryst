from django.urls import path
from . import views

urlpatterns = [
    path('adminlogin/', views.events_admin_login, name='events_admin_login'),
    path('google_login/', views.google_login, name='google_login'),
    path('profile/', views.manage_profile, name='manage_profile'),
    path("city/", views.get_cities, name="get_cities"),
    path("college/", views.get_colleges, name="get_colleges"),
    path("college/details/", views.get_college_details,
         name="get_college_details"),
    path('iitdlogin/', views.iitd_login, name='iitd_login'),
    path('profile/category/', views.get_user_profile_category, name='get_user_profile_category'),

]
