from __future__ import unicode_literals
from datetime import datetime, timedelta
from django.db.models import F
from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from webapp.models import Domande, Varianti, Test, Test_Domande_Varianti
from django.http import Http404
from django.contrib.auth import authenticate, login, logout 
from django.core.exceptions import SuspiciousOperation
from .forms import LoginForm, TestManualeForm, TestOrarioEsattoForm, TestSfidaManualeForm, TestSfidaOrarioEsattoForm, GruppiForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .services import reformat_date
from django.db.models import Q
from .models import *
from random import randint
from django.utils.datastructures import MultiValueDict
from django.core.serializers import serialize
import json
import random
import string

def Create_other_var(array):

    for _ in range(randint(4,10)):
        array.append(''.join(random.choices(string.ascii_lowercase, k=randint(6,13))))

    return array


# LOGIN
def log_in(req):

    logout(req)

    if req.method == 'POST':

        form = LoginForm(req.POST)
        
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(req, username=username, password=password)

            if user is not None:
                login(req, user)
                
                return redirect('home')
            else :
                messages.error(req, 'username o password non corretti')    
            
    return render(req, "login/login.html")


# HOME
@login_required(login_url='login')
def home(req):

    #Test.objects.all().delete()
    #TestsGroup.objects.all().delete()

    display_test_manuale = TestsGroup.objects.prefetch_related().filter(utente=req.user.id, tipo = 'manuale').values('idGruppi', 'dataOraInserimento', 'nrTest', 'nrGruppo', 'dataOraInizio', 'secondiRitardo')
    display_test_orario = TestsGroup.objects.prefetch_related().filter(utente=req.user.id, tipo = 'orario').values('idGruppi', 'dataOraInserimento', 'nrTest', 'nrGruppo')
    display_test_programmati = Test.objects.filter(tipo = 'programmato').values('idTest', 'dataOraInizio')

    gruppi_programmati = []
    for te in display_test_programmati:
        gruppi_programmati.append([te['idTest'], te['dataOraInizio']])

    chart_tests = Test.objects.filter(utente=req.user.id, dataOraFine__isnull=False).order_by('-dataOraInizio')
    chart_tests_json = serialize('json', chart_tests)
    
    gruppi_manuale = []
    gruppi_orario = []
    for test in display_test_manuale:
        count = 0
        primo_t = test['dataOraInizio'] + timedelta(0,  test['secondiRitardo'] )
        now = datetime.now()
        while now > primo_t:
            count += 1
            primo_t += timedelta(0,  test['secondiRitardo'] )
            print(now, primo_t)

        if test['nrTest'] - test['nrGruppo'] - count  > 0:
            gruppi_manuale.append([test['idGruppi'], test['nrTest'] - test['nrGruppo'] - count, test['dataOraInserimento'].strftime("%Y-%m-%d %H:%M:%S")])

    for t in display_test_orario:
        if t['nrTest'] - t['nrGruppo'] > 0:
            gruppi_orario.append([t['idGruppi'], t['nrTest'] - t['nrGruppo'], t['dataOraInserimento'].strftime("%Y-%m-%d %H:%M:%S")])

    return render(req, 'home/home.html', {'gruppi_manuale': gruppi_manuale[::-1], 'chart_tests': chart_tests_json , 'gruppi_orario' : gruppi_orario[::-1], 'gruppi_programmati' : gruppi_programmati[::-1] , 'zero' : 0})


@login_required(login_url='login')
def delete_all_user_test(req):

    TestsGroup.objects.filter(utente = req.user.id).delete()

    return home(req) 


def cancella_un_test(req, idGruppi):
    
    TestsGroup.objects.filter(idGruppi = idGruppi).delete()

    return home(req)



# TEST
@login_required(login_url='login')
def creazioneTest(req):
    testManualeForm = TestManualeForm()
    testOrarioEsattoForm = TestOrarioEsattoForm()
    context = {"creaTestManualeForm": testManualeForm, "creaTestOrarioEsattoForm": testOrarioEsattoForm}
    return render(req, 'test/creazioneTest.html', context)

@login_required(login_url='login')
def creaTestManuale(req):
    if req.method == 'POST':
        form = TestManualeForm(req.POST)
        mutable_data = MultiValueDict(form.data.lists())
        mutable_data['dataOraInizio'] = reformat_date(mutable_data['dataOraInizio'])
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

@login_required(login_url='login')
def TestStart(req, idGruppi, idTest, counter):

    ctx = []
    if Test.objects.filter(idTest = idTest).values('dataOraInizio')[0]['dataOraInizio'] is None:

        Test.objects.filter(idTest = idTest).update(dataOraInizio = datetime.now())

    
    ultimo = False
    if Test.objects.filter(idTest = idTest).values('nrGruppo')[0]['nrGruppo'] -1 <= counter:
        ultimo = True
    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda','variante')
    
    for domanda in test_to_render:
        
        var_to_app = Create_other_var([])
        ctx.append([domanda.domanda, var_to_app, domanda.variante])
    
        #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

    counter += 1
    ctx = ctx[(counter-1)*5:((counter)*5)]

    return render(req, 'preTest/TestSelect.html', {'ctx' : ctx,'idGruppi' : idGruppi,'idTest' : idTest, 'ultimo': ultimo, 'counter' : counter})

def preTest(req, idGruppi):


    TestsGroup.objects.filter(idGruppi = idGruppi).update(nrGruppo=F('nrGruppo') + 1)
    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('nrTest' , 'inSequenza', 'secondiRitardo', 'dataOraInizio', 'nrGruppo')
    nrTest = tests[0]['nrTest'] - tests[0]['nrGruppo']
    
    if(nrTest > 0):
        singolo_test = Test.objects.create(utente = req.user, nrGruppo = randint(2,3))
        domande = Domande.objects.prefetch_related()
        
        # Associa domande casuali con la relativa variante casuale al nuovo test creato
        for _ in range(15):

            random_domanda = randint(0, len(domande)-1)

            varianti = Varianti.objects.filter(domanda = domande[random_domanda])
            random_variante = randint(0, len(varianti) -1)

            Test_Domande_Varianti.objects.create(test = singolo_test, domanda = domande[random_domanda], variante = varianti[random_variante])

        return render(req, 'preTest/preTest.html', {'idGruppi' : idGruppi,'idTest' : singolo_test.idTest, 'nrTest' : nrTest, 'counter' : 0})

    else :

        return cancella_un_test(req, idGruppi)

def FinishTest(req, idGruppi, idTest):

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

    return render(req, 'preTest/FinishTest.html', {'idGruppi' : idGruppi ,'tempo' : tempo_finish})

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
        return cancella_un_test(req, idGruppi)


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

def TestProgrammati(req, idTest):
    return HttpResponse(idTest)

# SFIDE
def Sfida(req):
    user_list = User.objects.exclude(Q(id=1))
    user_fields_list = [{'id': user.id, 'username': user.username } for user in user_list]

    testSfidaManualeForm = TestSfidaManualeForm()
    testSfidaOrarioEsattoForm = TestSfidaOrarioEsattoForm()
    context = {
        'user_list': user_fields_list, 
        "creaTestSfidaManualeForm": testSfidaManualeForm, 
        "creaTestSfidaOrarioEsattoForm": testSfidaOrarioEsattoForm
        }

    return render(req, 'sfide/sfide.html', context)

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