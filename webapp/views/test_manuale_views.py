from __future__ import unicode_literals
from datetime import datetime
from django.db.models import F
from django.shortcuts import render, redirect
from webapp.models import Domande, Varianti, Test, Test_Domande_Varianti
from ..forms import TestManualeForm, TestSfidaManualeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from ..models import *
from random import randint
from . import test_common_views
from ..services import test_manuale_service
from ..utils import utils
from django.utils.datastructures import MultiValueDict

@login_required(login_url='login')
def creaTestManuale(req):
    if req.method == 'POST':
        form = TestManualeForm(req.POST)
        mutable_data = MultiValueDict(form.data.lists())
        mutable_data['dataOraInizio'] = utils.reformat_date(mutable_data['dataOraInizio'])
        form = TestManualeForm(mutable_data) 

        if form.is_valid():
            numeroTest = form.cleaned_data['numeroTest']
            secondiRitardo = form.cleaned_data['secondiRitardo']
            dataOraInizio = form.cleaned_data['dataOraInizio']
            try:
                with transaction.atomic():
                    TestsGroup.objects.create(utente = req.user, tipo='manuale', nrTest =numeroTest, secondiRitardo = secondiRitardo, dataOraInizio = dataOraInizio)

                messages.success(req, 'Test creati con successo.')

            except Exception as e:
                print(f"Errore durante la creazione del test: {e}")
                messages.error(req, "Errore durante creazione test: ", e)
        else: 
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(req, f"Errore: {error}")
            testManualeForm = TestManualeForm()
            testOrarioEsattoForm = form
            context = {"creaTestManualeForm": testManualeForm, "creaTestOrarioEsattoForm": testOrarioEsattoForm}
            return redirect('/creazione-test', context)

    return redirect('/home')




@login_required(login_url='login')
def TestStart(req, idGruppi, idTest, counter):

    ctx = []
    
    ultimo = False
    if Test.objects.filter(idTest = idTest).values('nrGruppo')[0]['nrGruppo'] - 1 <= counter:
        ultimo = True
    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda','variante')
    
    for domanda in test_to_render:
        
        var_to_app = utils.Create_other_var([])
        ctx.append([domanda.domanda, var_to_app, domanda.variante])
    
        #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

    ctx = ctx[(counter)*5:((counter+1)*5)]
    counter += 1
    return render(req, 'preTest/TestSelect.html', {'ctx' : ctx,'idGruppi' : idGruppi,'idTest' : idTest, 'ultimo': ultimo, 'counter' : counter})


def preTest(req, idGruppi, idTest):

    singolo_test =  Test.objects.filter(idTest = idTest)[0]

    if datetime.now() > singolo_test.dataOraInizio:
        
        TestsGroup.objects.filter(idGruppi = idGruppi).update(nrGruppo=F('nrGruppo') + 1)
        tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('nrTest' , 'inSequenza', 'secondiRitardo', 'dataOraInizio', 'nrGruppo')
        nrTest = tests[0]['nrTest'] - tests[0]['nrGruppo']
        
        if(nrTest >= 0):
            
            domande = Domande.objects.prefetch_related()
            varianti = Varianti.objects.prefetch_related()

            app_list = list()

            # Associa domande casuali con la relativa variante casuale al nuovo test creato
            for _ in range(15):

                random_domanda = randint(0, len(domande)-1)

                random_variante = randint(0, len(varianti) -1)

                app_list.append(Test_Domande_Varianti(test = singolo_test, domanda = domande[random_domanda], variante = varianti[random_variante]))
        
            Test_Domande_Varianti.objects.bulk_create(app_list)

            return redirect('TestStart' , idGruppi = idGruppi, idTest = idTest, counter = 0)

        else :

            return cancella_un_test(req, idGruppi)
    else : 
        
        return render(req, 'preTest/preTest.html', {'time_display' : singolo_test.dataOraInizio.strftime("%Y-%m-%d %H:%M:%S")})



def FinishTest(req, idGruppi, idTest):
        
    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('dataOraInizio', 'secondiRitardo')[0]

    test_finito = Test.objects.filter(idTest = idTest).values('dataOraInizio', 'secondiRitardo')[0]
    id_next_test = Test.objects.create(utente = req.user, dataOraInizio = test_finito['dataOraInizio'] + timedelta(0, tests['secondiRitardo']), nrGruppo = randint(2,3))
    TestsGroup.objects.filter(idGruppi = idGruppi).update(dataOraInizio = id_next_test.dataOraInizio)
    end =  Test.objects.filter(idTest = idTest).values('dataOraFine')[0]
    if end['dataOraFine'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraFine = datetime.now())
    tt = Test.objects.filter(idTest = idTest)
    tempo_test_finale = tt[0].dataOraFine.second
    tempo_test_iniziale = tt[0].dataOraInizio.second

    if tempo_test_finale < tempo_test_iniziale:
            tempo_finish = tempo_test_finale +60  - tempo_test_iniziale
    else:
        tempo_finish = tempo_test_finale - tempo_test_iniziale

    return render(req, 'preTest/FinishTest.html', {'idGruppi' : idGruppi ,'tempo' : tempo_finish, 'idTest' : id_next_test.idTest })


##### SFIDA #####
@login_required(login_url='login')
def creaTestSfidaManuale(req):
    if req.method == 'POST':
        form = TestSfidaManualeForm(req.POST)
        if form.is_valid():
            numeroTest = form.cleaned_data['numeroTest']
            
            try:
                with transaction.atomic():
                    TestsGroup.objects.create(utente = req.user, tipo='manuale', nrTest =numeroTest)

                messages.success(req, 'Test creati con successo.')

            except Exception as e:
                print(f"Errore durante la creazione del test: {e}")
                messages.error(req, "Errore durante creazione test: ", e)
        else: 
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(req, f"Errore: {error}")
            testSfidaManualeForm = TestSfidaManualeForm()
            testSfidaOrarioEsattoForm = form
            
            context = {
                "creaTestSfidaManualeForm": testSfidaManualeForm, 
                "creaTestSfidaOrarioEsattoForm": testSfidaOrarioEsattoForm
                }            
    return redirect('/Sfida', context)