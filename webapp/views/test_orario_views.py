from __future__ import unicode_literals
from datetime import datetime, timedelta
from django.db.models import F
from django.shortcuts import render, HttpResponse, redirect
from webapp.models import Domande, Varianti, Test, Test_Domande_Varianti
from ..forms import LoginForm, TestManualeForm, TestOrarioEsattoForm, TestSfidaManualeForm, TestSfidaOrarioEsattoForm, GruppiForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from ..models import *
from random import randint
from . import test_common_views

@login_required(login_url='login')
def creaTestOrarioEsatto(req):
    if req.method == 'POST':
        form = TestOrarioEsattoForm(req.POST)
        if form.is_valid():

            numeroTest = form.cleaned_data['numeroTest']
            secondiRitardo = form.cleaned_data['secondiRitardo']

            try:
                with transaction.atomic():
                    TestsGroup.objects.create(nrTest = numeroTest, utente = req.user, secondiRitardo=secondiRitardo, tipo='orario')

                print("Test creati con successo")
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



def CreazioneTestOrario(req, idGruppi, counter):

    TestsGroup.objects.filter(idGruppi = idGruppi).update(nrGruppo=F('nrGruppo') + 1)
    singolo_test = Test.objects.create(utente = req.user, nrGruppo = randint(2,3))
    domande = Domande.objects.prefetch_related()
    varianti = Varianti.objects.prefetch_related()
    app_list = list()
    for _ in range(15):

        random_domanda = randint(0, len(domande)-1)


        random_variante = randint(0, len(varianti) -1)

        app_list.append(Test_Domande_Varianti(test = singolo_test, domanda = domande[random_domanda], variante = varianti[random_variante]))
        
    Test_Domande_Varianti.objects.bulk_create(app_list)
    return redirect('preTestOrario' , idGruppi = idGruppi, idTest = singolo_test.idTest, counter = counter)



def preTestOrario(req, idGruppi, idTest, counter):

    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('nrTest' , 'secondiRitardo', 'dataOraInizio', 'nrGruppo')
    test = Test.objects.filter(idTest = idTest).values( 'secondiRitardo', 'dataOraInizio', 'nrGruppo')
    if test[0]['dataOraInizio'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraInizio = datetime.now() + timedelta(0,tests[0]['secondiRitardo']))
        return preTestOrario(req, idGruppi, idTest, counter)
    
    nrTest = tests[0]['nrTest'] - tests[0]['nrGruppo']
    #singolo_test = Test.objects.filter(idTest = idTest)[0]

    if nrTest >= 0 : 
        if(datetime.now() < test[0]['dataOraInizio']):
            return render(req, 'preTestOrario/preTestOrario.html', {'time_display' : test[0]['dataOraInizio'].strftime("%Y-%m-%d %H:%M:%S")})
        else:

            return redirect('testStartOrario', idGruppi = idGruppi, idTest=idTest, counter = counter, displayer = 0)
    else:
        return test_common_views.cancella_un_test(req, idGruppi)


def testStartOrario(req, idGruppi, idTest, counter, displayer):

    TestsGroup.objects.filter(idGruppi = idGruppi).update(dataOraInizio = None)
    ultimo = False
    test = Test.objects.filter(idTest = idTest).values('nrGruppo', 'dataOraInizio')[0]
    if test['nrGruppo'] -1 <= displayer:
        ultimo = True
    ctx = []
    if test['dataOraInizio'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraInizio = datetime.now())
    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda','variante')
    
    for domanda in test_to_render:
        
        ctx.append([domanda.domanda, domanda.variante])
    
        #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

    ctx = ctx[(displayer)*5:((displayer+1)*5)]
    displayer += 1
    if req.method == 'POST':
        form = GruppiForm(req.POST, 15, idTest)
        if form.is_valid():
            for i in range(len(form)):
                risposta = form.cleaned_data['domanda_{}'.format(i)]
                print(form)
        else:
            print('amamamama')
    return render(req, 'preTestOrario/TestSelect.html', {'ctx' : ctx,'idGruppi' : idGruppi, 'ultimo' : ultimo, 'idTest' : idTest, 'counter' : counter, 'displayer' : displayer})



def FinishTestOrario(req, idGruppi, idTest, counter):

    counter += 1
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

    return render(req, 'preTestOrario/FinishTest.html', {'idGruppi' : idGruppi ,'tempo' : tempo_finish, 'counter' : counter})


##### SFIDA #####

@login_required(login_url='login')
def creaTestSfidaOrarioEsatto(req):
    if req.method == 'POST':
        form = TestSfidaOrarioEsattoForm(req.POST)
        if form.is_valid():

            numeroTest = form.cleaned_data['numeroTest']
            secondiRitardo = form.cleaned_data['secondiRitardo']

            try:
                with transaction.atomic():
                    TestsGroup.objects.create(nrTest = numeroTest, utente = req.user, secondiRitardo=secondiRitardo, tipo='orario')

                print("Test creati con successo")
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


