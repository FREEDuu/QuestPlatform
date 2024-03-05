from django.urls import path

from . import views
from .views import test_common_views, test_manuale_views, test_orario_views, page_views

urlpatterns = [
    
    path('login/' , page_views.log_in, name= 'login'),
    path('' , page_views.home, name= 'home'),
    path('home' , page_views.home, name= 'home'),
    path('testCollettivi' , page_views.testCollettivi, name= 'testCollettivi'),
    path('creaTestCollettivo/<int:pagine>/<int:idTest>' , page_views.creaTestCollettivo, name= 'creaTestCollettivo'),
    path('creaTestCollettivoDisplay/<int:idTest>/<int:n>' , page_views.creaTestCollettivoDisplay, name= 'creaTestCollettivoDisplay'),
    path('creazione-test' , page_views.creazioneTest, name= 'test'),
    path('crea-test-manuale' , test_manuale_views.creaTestManuale, name= 'creaTestManuale'),
    path('crea-test-sfida-manuale' , test_manuale_views.creaTestSfidaManuale, name= 'creaTestSfidaManuale'),
    path('crea-test-orario-esatto' , test_orario_views.creaTestOrarioEsatto, name= 'creaTestOrarioEsatto'),
    path('crea-test-sfida-orario-esatto' , test_orario_views.creaTestSfidaOrarioEsatto, name= 'creaTestSfidaOrarioEsatto'),
    path('cancella-test', test_common_views.delete_all_user_test, name='delete_all_user_test'),
    path('cancella-un-test/<int:idGruppi>' , test_common_views.cancella_un_test, name = 'cancella_un_test'),
    path('preTest/<int:idGruppi>/<int:idTest>' , test_manuale_views.preTest, name= 'preTest'),
    path('preTestOrario/<int:idGruppi>/<int:idTest>/<int:counter>' , test_orario_views.preTestOrario, name= 'preTestOrario'),
    path('testStart/<int:idGruppi>/<int:idTest>/<int:counter>/<int:seed>' , test_manuale_views.TestStart, name= 'TestStart'),
    path('testStartOrario/<int:idGruppi>/<int:idTest>/<int:counter>/<int:displayer>/<int:seed>' , test_orario_views.testStartOrario, name= 'testStartOrario'),
    path('FinishTest/<int:idGruppi>/<int:idTest>' , test_manuale_views.FinishTest, name= 'FinishTest'),
    path('FinishTestOrario/<int:idGruppi>/<int:idTest>/<int:counter>/' , test_orario_views.FinishTestOrario, name= 'FinishTestOrario'),
    path('testProgrammati/<int:idTest>', test_common_views.TestProgrammati, name = 'TestProgrammati'),
    path('testProgrammatiStart/<int:idTest>/<int:counter>', test_common_views.TestProgrammatiStart, name = 'TestProgrammatiStart'),
    path('testProgrammatiFinish/<int:idTest>', test_common_views.TestProgrammatiFinish, name = 'TestProgrammatiFinish'),
    path('statistiche', page_views.statistiche, name = 'statistiche'),
    path('Sfida', page_views.Sfida, name = 'Sfida'),
    path('preTestSfida/<int:idGruppi>/<int:id>', test_orario_views.preTestSfida, name = 'preTestSfida'),
    path('testStartOrarioSfida/<int:idTest>/<int:displayer>', test_orario_views.testStartOrarioSfida, name = 'testStartOrarioSfida'),
    path('FinishTestOrarioSfida/<int:idTest>', test_orario_views.FinishTestOrarioSfida, name = 'FinishTestOrarioSfida'),
    path('CreazioneTestOrario/<int:idGruppi>/<int:counter>' , test_orario_views.CreazioneTestOrario, name = 'CreazioneTestOrario')
]