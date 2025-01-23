from django.urls import path
from . import views

urlpatterns = [
    path('dump/', views.dump, name='dump'),
    path('details/', views.details, name='details'),
    path('events/', views.events, name='events'),
    path('events/poster/', views.updatePoster, name='updatePoster'),
    path('events/download/', views.download, name='download'),
    path('speaker/', views.speaker, name='speaker'),
    path('speaker/image/', views.updateImage, name='updateImage'),
    path('accommodation/', views.accommodation, name='accommodation'),
    path('accommodation/confirm/', views.accConfirm, name='accConfirm'),
    path('accommodation/download/', views.accDownload, name='accDownload'),
    path('merchandise/', views.merchandise, name='merchandise'),
    path('merchandise/confirm/', views.merchConfirm, name='merchConfirm'),
    path('merchandise/download/', views.merchDownload, name='merchDownload'),
    path('merchandise/download/internal/',
         views.merchDownloadInternal, name='merchDownloadInternal'),
    path('passes/', views.passes, name='passes'),
    path('passes/enter/', views.enterPasses, name='enterPasses'),
    path('passes/internal/', views.internalPass, name='internalPass'),
]
