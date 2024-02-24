from __future__ import unicode_literals
from datetime import datetime, timedelta
from django.db.models import F
from django.shortcuts import render, HttpResponse, redirect
from webapp.models import Domande, Varianti, Test, Test_Domande_Varianti
from ..forms import LoginForm, TestManualeForm, TestOrarioEsattoForm, TestSfidaManualeForm, TestSfidaOrarioEsattoForm, FormDomandaCollettiva, FormDomanda
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from ..models import *
from random import randint
import random
from . import test_common_views
from django.db.models.query import QuerySet

def genRandomFromSeed(seed, rispostaGiusta):
    random.seed(seed)
    ret = [('1',str(randint(0,9))),('2',str(randint(0,8))),(str(rispostaGiusta), str(rispostaGiusta))]
    random.shuffle(ret)
    return ret , seed+1


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

    app_list = list()

    for _ in range(15):

        random_domanda = randint(0, len(domande)-1)
        varianti = Varianti.objects.filter(domanda = domande[random_domanda])

        app_list.append(Test_Domande_Varianti(test = singolo_test, domanda = domande[random_domanda], variante = varianti[randint(0, len(varianti)-1)]))
        
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
            TestsGroup.objects.filter(idGruppi = idGruppi).update(dataOraInizio = None)
            return redirect('testStartOrario', idGruppi = idGruppi, idTest=idTest, counter = counter, displayer = 0, seed = randint(0,1000))
    else:
        return test_common_views.cancella_un_test(req, idGruppi)

def testStartOrario(req, idGruppi, idTest, counter, displayer , seed):

    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda','variante')
    test_to_render1 = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda')

    domande_to_render = []

    ultimo = False
    test = Test.objects.filter(idTest = idTest).values('nrGruppo', 'dataOraInizio')[0]
    if test['nrGruppo'] -1 <= displayer:
        ultimo = True

    for d in test_to_render1:
        domande_to_render.append(Domande.objects.filter(idDomanda = d.domanda.idDomanda).values('tipo')[0]['tipo'])
    ctx = []
    if req.method == 'POST':

        formRisposta = FormDomanda(domande_to_render, req.POST)
        check = False
        for n in range((displayer-1)*5, ((displayer)*5)):
      
            if req.POST['domanda_{}'.format(n)] != test_to_render[n].variante.rispostaEsatta:
                if n >= displayer *5 and n < (displayer+1) * 5 :
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante,formRisposta['domanda_{}'.format(n)], True])
                    check = True
            else :
                if n >= displayer *5 and n < (displayer+1) * 5 : 
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante,formRisposta['domanda_{}'.format(n)], False])

        if check:
            for n in range(len(test_to_render)):
                if n >= displayer *5 and n < (displayer+1) * 5 :
                    formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
          
            return render(req, 'preTestOrario/TestSelect.html', {'idGruppi' : idGruppi, 'ultimo' : ultimo, 'idTest' : idTest, 'counter' : counter, 'displayer' : displayer, 'ctx' : ctx , 'seed' : seed})
        else : 
            
            for n in range(len(test_to_render)):
                if n >= displayer *5 and n < (displayer+1) * 5 :

                    formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante,formRisposta['domanda_{}'.format(n)], False])

                #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale)
            displayer += 1
            return render(req, 'preTestOrario/TestSelect.html', {'idGruppi' : idGruppi, 'ultimo' : ultimo, 'idTest' : idTest, 'counter' : counter, 'displayer' : displayer, 'ctx' : ctx , 'seed' : seed})

    else:

        forms = FormDomanda(domande_to_render)
        
        for n in range(len(test_to_render)):
            if n >= displayer *5 and n < (displayer+1) * 5 : 
                forms.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante,forms['domanda_{}'.format(n)], False])

            #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale)
        return render(req, 'preTestOrario/TestSelect.html', {'idGruppi' : idGruppi, 'ultimo' : ultimo, 'idTest' : idTest, 'counter' : counter, 'displayer' : displayer+1, 'ctx' : ctx , 'seed' : seed})


def FinishTestOrario(req, idGruppi, idTest,displayer, counter, seed):

    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda','variante')
    test_to_render1 = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda')
    domande_to_render = []
    ultimo = False
    test = Test.objects.filter(idTest = idTest).values('nrGruppo', 'dataOraInizio')[0]
    if test['nrGruppo'] -1 == displayer:
        ultimo = True
    for d in test_to_render1:
        domande_to_render.append(Domande.objects.filter(idDomanda = d.domanda.idDomanda).values('tipo')[0]['tipo'])
    if req.method == 'POST':
        ctx = []
        formRisposta = FormDomanda(domande_to_render, req.POST)
        check = False
        for n in range((displayer-1)*5, ((displayer)*5)):

            if req.POST['domanda_{}'.format(n)] != test_to_render[n].variante.rispostaEsatta:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante,formRisposta['domanda_{}'.format(n)], True])
                check = True
            else : 
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante,formRisposta['domanda_{}'.format(n)], False])
        
        if check:
            print('QUII')
            return render(req, 'preTestOrario/TestSelect.html', {'idGruppi' : idGruppi, 'ultimo' : ultimo, 'idTest' : idTest, 'counter' : counter, 'displayer' : displayer, 'ctx' : ctx[(displayer)*5:(displayer+1)*5] , 'seed' : seed})
        
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


