from django.urls import path

from . import views
from .views import test_common_views, test_manuale_views, test_orario_views, page_views

urlpatterns = [
    
    path('login/' , page_views.log_in, name= 'login'),
    path('creaDomande' , page_views.creaDomande, name= 'creaDomande'),
    path('creaDomandeDisplay' , page_views.creaDomandeDisplay, name= 'creaDomandeDisplay'),
    path('accettaSfida/<int:idGruppi>/<int:id>' , page_views.accettaSfida, name= 'accettaSfida'), 
    path('rifiutaSfida/<int:idGruppi>/<int:id>' , page_views.rifiutaSfida, name= 'rifiutaSfida'),     
    path('' , page_views.home, name= 'home'),
    path('home' , page_views.home, name= 'home'),
    path('controllo' , page_views.controllo, name= 'controllo'),
    path('csv-riepilogo_test' , page_views.csv_riepilogo_test, name= 'csv_riepilogo_test'),
    path('csv_riepilogo_ultimo_collettivo' , page_views.csv_riepilogo_ultimo_collettivo, name= 'csv_riepilogo_ultimo_collettivo'),
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
    path('testStart/<int:idGruppi>/<int:idTest>/<int:counter>/<int:seed>/<int:num>' , test_manuale_views.TestStart, name= 'TestStart'),
    path('testStartOrario/<int:idGruppi>/<int:idTest>/<int:counter>/<int:displayer>/<int:seed>' , test_orario_views.testStartOrario, name= 'testStartOrario'),
    path('FinishTest/<int:idGruppi>/<int:idTest>' , test_manuale_views.FinishTest, name= 'FinishTest'),
    path('FinishTestOrario/<int:idGruppi>/<int:idTest>/<int:counter>/<int:seed>' , test_orario_views.FinishTestOrario, name= 'FinishTestOrario'),
    path('testProgrammati/<int:idTest>', test_common_views.TestProgrammati, name = 'TestProgrammati'),
    path('testProgrammatiStart/<int:idTest>/<int:counter>', test_common_views.TestProgrammatiStart, name = 'TestProgrammatiStart'),
    path('testProgrammatiFinish/<int:idTest>', test_common_views.TestProgrammatiFinish, name = 'TestProgrammatiFinish'),
    path('statistiche', page_views.statistiche, name = 'statistiche'),
    path('Sfida', page_views.Sfida, name = 'Sfida'),
    path('preTestSfida/<int:idGruppi>/<int:idTestSfida>', test_orario_views.preTestSfida, name = 'preTestSfida'),
    path('testStartOrarioSfida/<int:idTest>/<int:displayer>/<int:idTestSfida>', test_orario_views.testStartOrarioSfida, name = 'testStartOrarioSfida'),
    path('FinishTestOrarioSfida/<int:idTest>/<int:idTestSfida>', test_orario_views.FinishTestOrarioSfida, name = 'FinishTestOrarioSfida'),
    path('CreazioneTestOrario/<int:idGruppi>/<int:counter>' , test_orario_views.CreazioneTestOrario, name = 'CreazioneTestOrario'),
    path('RiepilogoTest/<int:idGruppi>/<int:idTest>/<int:counter>/<int:seed>', page_views.RiepilogoTest, name = 'RiepilogoTest'),
    path('exit-test', page_views.esciDalTest, name = 'exit-test'),
    path('setVisibilitaCollettivi/', page_views.setVisibilitaCollettivi, name='setVisibilitaCollettivi'),
    path('api/make_domande/<str:CorpoDomanda>/<str:tipo>/<str:VariantiCorpo>/<str:VariantiRisposta>', page_views.make_domande, name='make_domande'),
    path('api/get_domande', page_views.get_domande, name='get_domande')
]