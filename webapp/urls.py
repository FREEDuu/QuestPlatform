from django.urls import path

from . import views

urlpatterns = [
    path('login/' , views.log_in, name= 'login'),
    path('' , views.home, name= 'home'),
    path('home' , views.home, name= 'home'),
    path('creazione-test' , views.creazioneTest, name= 'test'),
    path('preTest/<int:test_id>' , views.preTest, name= 'preTest')
]