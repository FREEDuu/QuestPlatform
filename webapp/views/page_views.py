from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.db.models import F
from webapp.models import Test 
from django.contrib.auth import authenticate, login, logout 
from ..forms import LoginForm, TestManualeForm, TestOrarioEsattoForm, TestSfidaManualeForm, TestSfidaOrarioEsattoForm, FormTestCollettivi, FormDomandaCollettiva
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from ..models import *
from django.core.serializers import serialize
from datetime import datetime, timedelta
from random import randint
from django.utils.datastructures import MultiValueDict
from ..utils import utils



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
    #Varianti.objects.all().delete()
    #Domande.objects.filter(tipo = 's').delete()
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
        primo_t = test['dataOraInizio']
        now = datetime.now()
        if(now > primo_t):
            while now > primo_t:
                count += 1
                primo_t += timedelta(0,  test['secondiRitardo'])
                print(now, primo_t)
            TestsGroup.objects.filter(idGruppi = test['idGruppi']).update(dataOraInizio = primo_t)
        
        TestsGroup.objects.filter(idGruppi = test['idGruppi']).update(nrGruppo=F('nrGruppo') + count)
        test_manuale_esatto = Test.objects.create(utente = req.user, dataOraInizio = primo_t, secondiRitardo = test['secondiRitardo'], nrGruppo = randint(2,3))
        nrgruppo = TestsGroup.objects.filter(idGruppi = test['idGruppi']).values('nrGruppo','dataOraInizio')[0]
        if test['nrTest'] -  nrgruppo['nrGruppo'] > 0:
            gruppi_manuale.append([test['idGruppi'], test['nrTest'] - nrgruppo['nrGruppo' ], nrgruppo['dataOraInizio'].strftime("%Y-%m-%d %H:%M:%S"),test_manuale_esatto.idTest ])
    for t in display_test_orario:
        if t['nrTest'] - t['nrGruppo'] > 0:
            gruppi_orario.append([t['idGruppi'], t['nrTest'] - t['nrGruppo'], t['dataOraInserimento'].strftime("%Y-%m-%d %H:%M:%S")])
    return render(req, 'home/home.html', {'gruppi_manuale': gruppi_manuale[::-1], 'chart_tests': chart_tests_json , 'gruppi_orario' : gruppi_orario[::-1], 'gruppi_programmati' : gruppi_programmati[::-1] , 'zero' : 0})




@login_required(login_url='login')
def creazioneTest(req):
    testManualeForm = TestManualeForm()
    testOrarioEsattoForm = TestOrarioEsattoForm()
    context = {"creaTestManualeForm": testManualeForm, "creaTestOrarioEsattoForm": testOrarioEsattoForm}
    return render(req, 'test/creazioneTest.html', context)



@login_required(login_url='login')
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


def testCollettivi(req):

    ctx = {'form' : FormTestCollettivi(), 'prima' : True}

    return render(req, 'test/testCollettivi.html', ctx)

def creaTestCollettivo(req):

    if req.method == 'POST':

        form = FormTestCollettivi(req.POST)
        mutable_data = MultiValueDict(form.data.lists())
        mutable_data['ora'] = utils.reformat_date(mutable_data['ora'])
        form = FormTestCollettivi(mutable_data) 
        if form.is_valid():

            nPagine = form.cleaned_data['nPagine']
            dataOraInizio = form.cleaned_data['ora']
            #test_collettivo = Test.objects.create(utente = req.user , dataOraInizio = dataOraInizio, nrGruppo = nPagine)
            
            return render(req, 'test/testCollettivi.html', {'domande' : range(1, nPagine+1)})
        else: 
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(req, f"Errore: {error}")
            print(form.errors)
            return testCollettivi(req)

def creaTestCollettivoDisplay(req):
    if req.method == 'POST':

        form = FormDomandaCollettiva(req.POST)
        if form.is_valid():

            domanda = form.cleaned_data['Domanda']
            risposta = form.cleaned_data['Risposta']
            varianti = form.cleaned_data['Varianti']
            print(domanda, risposta, varianti)
            return HttpResponse(risposta+varianti+domanda)

    return render(req, 'test/displayDomanda.html', {'form' : FormDomandaCollettiva()})