from django.urls import path

from . import views

urlpatterns = [
    path('login/' , views.log_in, name= 'login'),
    path('' , views.home, name= 'home'),
    path('home' , views.home, name= 'home'),
    path('creazione-test' , views.creazioneTest, name= 'test'),
    path('crea-test-manuale' , views.creaTestManuale, name= 'creaTestManuale'),
    path('crea-test-orario-esatto' , views.creaTestOrarioEsatto, name= 'creaTestOrarioEsatto'),
    path('cancella-test', views.delete_all_user_test, name='delete_all_user_test'),
    path('cancella-un-test/<int:idGruppi>' , views.cancella_un_test, name = 'cancella_un_test'),
    path('preTest/<int:idGruppi>/<int:counter>/' , views.preTest, name= 'preTest')
]