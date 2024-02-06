from __future__ import unicode_literals

from datetime import datetime
from django.db.models import F
from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from webapp.models import Domande, Varianti, Test, Test_Domande_Varianti
from django.http import Http404
from django.contrib.auth import authenticate, login, logout 
from django.core.exceptions import SuspiciousOperation
from .forms import LoginForm, TestManualeForm, TestOrarioEsattoForm, GruppiForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .services import reformat_date
from .models import *
from random import randint
from django.utils.datastructures import MultiValueDict



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
    
    '''
    for _ in range(5):
        TestsGroup.objects.create(utente = req.user, inSequenza=True, tipo='manuale', nrTest =100)
        '''
    #Test.objects.all().delete()
    display_test = TestsGroup.objects.prefetch_related().filter(utente = req.user.id).values('idGruppi', 'dataOraInserimento', 'nrTest', 'nrGruppo')
    gruppi = []

    for test in display_test:
        

        gruppi.append([test['idGruppi'] ,test['nrTest']- test['nrGruppo'], test['dataOraInserimento'].strftime("%Y-%m-%d %H:%M:%S")])         


    return render(req, 'home/home.html', {'gruppi' : gruppi[::-1], 'zero' : 0})

@login_required(login_url='login')
def delete_all_user_test(req):

    TestsGroup.objects.filter(utente = req.user.id).delete()

    return render(req, 'home/home.html') 

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
        if form.is_valid():
            numeroTest = form.cleaned_data['numeroTest']
            inSequenza = form.cleaned_data['inSequenza']
            secondiRitardo = form.cleaned_data['secondiRitardo']

            # Ricava il numero univoco per raggruppare i nuovi test da creare

            try:
                with transaction.atomic():
                    TestsGroup.objects.create(utente = req.user, inSequenza=inSequenza, secondiRitardo=secondiRitardo, tipo='manuale', nrTest =numeroTest)
                        # Associa il test all'utente loggato
                '''
                        for _ in range(10):
                            # Scegli una domanda random 
                            idDomandaCasuale = Domande.get_random_domanda().idDomanda
                            #print(f"Selected idDomandaCasuale: {idDomandaCasuale}")
                            # Scegli una variante random 
                            idVarianteCasuale = Varianti.get_random_variante(idDomandaCasuale).idVariante
                            #print(f"Selected idVarianteCasuale: {idVarianteCasuale}")
                            # Associa domanda e variante al nuovo test creato
                            Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

                        '''

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
        # I dati nella post request sono immutabili, quindi per modificarli bisogna copiarli in un nuovo oggetto
        form = TestOrarioEsattoForm(req.POST)
        mutable_data = MultiValueDict(form.data.lists())
        mutable_data['dataOraInizio'] = reformat_date(mutable_data['dataOraInizio'])
        form = TestOrarioEsattoForm(mutable_data) 

        if form.is_valid():
            numeroTest = form.cleaned_data['numeroTest']
            inSequenza = form.cleaned_data['inSequenza']
            secondiRitardo = form.cleaned_data['secondiRitardo']
            dataOraInizio = form.cleaned_data['dataOraInizio']
            nrGruppo=Test.get_next_gruppo()

            try:
                with transaction.atomic():
                    # Crea i test
                    for _ in range(numeroTest):
                        nuovo_test = Test.objects.create(nrGruppo=nrGruppo, utente = req.user, inSequenza=inSequenza, secondiRitardo=secondiRitardo, dataOraInizio=dataOraInizio, tipo='orario')
                        # Associa domande casuali con la relativa variante casuale al nuovo test creato
                        for _ in range(10):
                            # Scegli una domanda random 
                            idDomandaCasuale = Domande.get_random_domanda().idDomanda
                            #print(f"Selected idDomandaCasuale: {idDomandaCasuale}")
                            print(secondiRitardo)
                            # Scegli una variante random 
                            idVarianteCasuale = Varianti.get_random_variante(idDomandaCasuale).idVariante
                            #print(f"Selected idVarianteCasuale: {idVarianteCasuale}")
                            # Associa domanda e variante al nuovo test creato
                            Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

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

def TestStart(req, idGruppi, idTest):

    ctx = []
    Test.objects.filter(idTest = idTest).update(dataOraInizio = datetime.now())
    print(datetime.now(),'ORA INIZIO TEST')
    TestsGroup.objects.filter(idGruppi = idGruppi).update(nrGruppo=F('nrGruppo') + 1)
    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda','variante')
    
    for domanda in test_to_render:
        
        ctx.append([domanda.domanda, domanda.variante])
    
        #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))



    return render(req, 'preTest/TestSelect.html', {'ctx' : ctx,'idGruppi' : idGruppi,'idTest' : idTest})

def preTest(req, idGruppi):

    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('nrTest' , 'inSequenza', 'secondiRitardo', 'dataOraInizio', 'nrGruppo')
    nrTest = tests[0]['nrTest'] - tests[0]['nrGruppo']

    if(nrTest > 0):

        singolo_test = Test.objects.create(utente = req.user)

        
        domande = Domande.objects.prefetch_related()

    # Associa domande casuali con la relativa variante casuale al nuovo test creato
        for _ in range(3):

            random_domanda = randint(0, len(domande)-1)

            varianti = Varianti.objects.filter(domanda = domande[random_domanda])

            random_variante = randint(0, len(varianti) -1)

            Test_Domande_Varianti.objects.create(test = singolo_test, domanda = domande[random_domanda], variante = varianti[random_variante])

        return render(req, 'preTest/preTest.html', {'idGruppi' : idGruppi,'idTest' : singolo_test.idTest, 'nrTest' : nrTest})

    else :

        return cancella_un_test(req, idGruppi)

def FinishTest(req, idGruppi, idTest):

    Test.objects.filter(idTest = idTest).update(dataOraInserimento = datetime.now())
    tt = Test.objects.filter(idTest = idTest)
    tempo_test_finale = tt[0].dataOraInserimento.second
    tempo_test_iniziale = tt[0].dataOraInizio.second

    if tempo_test_finale < tempo_test_iniziale:
            tempo_finish = tempo_test_finale +60  - tempo_test_iniziale
    else:
        tempo_finish = tempo_test_finale - tempo_test_iniziale

    return render(req, 'preTest/FinishTest.html', {'idGruppi' : idGruppi ,'tempo' : tempo_finish})