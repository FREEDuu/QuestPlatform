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
    path('preTest/<int:idGruppi>/' , views.preTest, name= 'preTest'),
    path('preTestOrario/<int:idGruppi>' , views.preTestOrario, name= 'preTestOrario'),
    path('testStart/<int:idGruppi>/<int:idTest>' , views.TestStart, name= 'TestStart'),
    path('preTestOrario/testStartOrario/<int:idGruppi>/<int:idTest>' , views.testStartOrario, name= 'testStartOrario'),
    path('FinishTest/<int:idGruppi>/<int:idTest>' , views.FinishTest, name= 'FinishTest'),
    path('FinishTestOrario/<int:idGruppi>/<int:idTest>' , views.FinishTestOrario, name= 'FinishTestOrario')



]