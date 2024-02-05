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
    
    display_test = TestsGroup.objects.prefetch_related().filter(utente = req.user.id).values('idGruppi', 'dataOraInserimento', 'nrTest')
    gruppi = {}
    date = {}

    for test in display_test:
        if(test['idGruppi'] not in gruppi.keys()):
            gruppi[test['idGruppi']] = test['nrTest']
            
        else:
            pass

    print(gruppi)
    return render(req, 'home/home.html', {'gruppi' : gruppi, 'date' : '#TODO', 'zero' : 0})

@login_required(login_url='login')
def delete_all_user_test(req):

    TestsGroup.objects.filter(utente = req.user.id).delete()

    return render(req, 'home/home.html') 

def cancella_un_test(req, idGruppi):
    
    TestsGroup.objects.filter(idGruppi = idGruppi).delete()
    print(idGruppi
    
    )

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
            nrGruppo=Test.get_next_gruppo()

            try:
                with transaction.atomic():
                    TestsGroup.objects.create(nrGruppo=nrGruppo, utente = req.user, inSequenza=inSequenza, secondiRitardo=secondiRitardo, tipo='manuale', nrTest =numeroTest)
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
def preTest(req, idGruppi, counter):

    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('nrTest' , 'inSequenza', 'secondiRitardo', 'dataOraInizio')
    nrTest = tests[0]['nrTest']
    ctx = []
    counter += 1
    nuovo_test = Test.objects.create( utente = req.user, inSequenza= tests[0]['inSequenza'], secondiRitardo=tests[0]['secondiRitardo'], dataOraInizio=tests[0]['dataOraInizio'], tipo='orario')

 # Associa domande casuali con la relativa variante casuale al nuovo test creato
    for _ in range(10):
                            # Scegli una domanda random 
        idDomandaCasuale = Domande.get_random_domanda().idDomanda
                            #print(f"Selected idDomandaCasuale: {idDomandaCasuale}")
                            # Scegli una variante random 
        idVarianteCasuale = Varianti.get_random_variante(idDomandaCasuale).idVariante
                            #print(f"Selected idVarianteCasuale: {idVarianteCasuale}")
                            # Associa domanda e variante al nuovo test creato
        Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

    forms = Test_Domande_Varianti.objects.filter(test = nuovo_test)

    if counter <= nrTest : 
        
        ctx = []

        for form in forms:

            ctx.append([form.domanda, form.variante])
    else :
        ctx = []
    

    return render(req, 'preTest/preTest.html', {'ctx' : ctx, 'counter' : counter, 'idGruppi' : idGruppi, 'nrTest' : nrTest})
