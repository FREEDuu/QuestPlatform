from django.urls import path

from . import views
from .views import test_common_views, test_manuale_views, test_orario_views, page_views

urlpatterns = [
    path('login/' , page_views.log_in, name= 'login'),
    path('' , page_views.home, name= 'home'),
    path('home' , page_views.home, name= 'home'),
    path('testCollettivi' , page_views.testCollettivi, name= 'testCollettivi'),
    path('creaTestCollettivo' , page_views.creaTestCollettivo, name= 'creaTestCollettivo'),
    path('creaTestCollettivoDisplay' , page_views.creaTestCollettivoDisplay, name= 'creaTestCollettivoDisplay'),
    path('creazione-test' , page_views.creazioneTest, name= 'test'),
    path('crea-test-manuale' , test_manuale_views.creaTestManuale, name= 'creaTestManuale'),
    path('crea-test-sfida-manuale' , test_manuale_views.creaTestSfidaManuale, name= 'creaTestSfidaManuale'),
    path('crea-test-orario-esatto' , test_orario_views.creaTestOrarioEsatto, name= 'creaTestOrarioEsatto'),
    path('crea-test-sfida-orario-esatto' , test_orario_views.creaTestSfidaOrarioEsatto, name= 'creaTestSfidaOrarioEsatto'),
    path('cancella-test', test_common_views.delete_all_user_test, name='delete_all_user_test'),
    path('cancella-un-test/<int:idGruppi>' , test_common_views.cancella_un_test, name = 'cancella_un_test'),
    path('preTest/<int:idGruppi>/<int:idTest>' , test_manuale_views.preTest, name= 'preTest'),
    path('preTestOrario/<int:idGruppi>/<int:idTest>/<int:counter>' , test_orario_views.preTestOrario, name= 'preTestOrario'),
    path('testStart/<int:idGruppi>/<int:idTest>/<int:counter>' , test_manuale_views.TestStart, name= 'TestStart'),
    path('testStartOrario/<int:idGruppi>/<int:idTest>/<int:counter>/<int:displayer>/<int:seed>' , test_orario_views.testStartOrario, name= 'testStartOrario'),
    path('FinishTest/<int:idGruppi>/<int:idTest>' , test_manuale_views.FinishTest, name= 'FinishTest'),
    path('FinishTestOrario/<int:idGruppi>/<int:idTest>/<int:displayer>/<int:counter>/<int:seed>' , test_orario_views.FinishTestOrario, name= 'FinishTestOrario'),
    path('testProgrammati/<int:idTest>', test_common_views.TestProgrammati, name = 'TestProgrammati'),
    path('Sfida', page_views.Sfida, name = 'Sfida'),
    path('CreazioneTestOrario/<int:idGruppi>/<int:counter>' , test_orario_views.CreazioneTestOrario, name = 'CreazioneTestOrario')


]