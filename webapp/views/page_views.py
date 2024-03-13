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
import plotly_express as px



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
    #Test.objects.filter(tipo = 'collettivo').delete()
    #Domande.objects.filter().delete()
    '''
    Domande.objects.create(corpo = 'Cavallo Bianco di Napoleone ? ' , tipo = 's')
    Domande.objects.create(corpo = 'Cavallo Bianco di Napoleone ? ' , tipo = 't')
    Domande.objects.create(corpo = 'Cavallo Bianco di Napoleone ? ' , tipo = 'c')
    Domande.objects.create(corpo = 'Cavallo Bianco di Napoleone ? ' , tipo = 'm')
    domandone = Domande.objects.all()

    for domandona in domandone :
        Varianti.objects.create(domanda = domandona, corpo = 'BIANCO', rispostaEsatta = 'bianco')
    '''
    if len(Statistiche.objects.filter(utente = req.user, tipoDomanda = 'stelle')) == 0:
        Statistiche.objects.create(utente = req.user, tipoDomanda = 'stelle', nrErrori = 0)
        Statistiche.objects.create(utente = req.user, tipoDomanda = 't', nrErrori = 0)
        Statistiche.objects.create(utente = req.user, tipoDomanda = 's', nrErrori = 0)
        Statistiche.objects.create(utente = req.user, tipoDomanda = 'r', nrErrori = 0)

    stelle = Statistiche.objects.filter(utente = req.user, tipoDomanda = 'stelle')[0].nrErrori

    display_test_manuale = TestsGroup.objects.select_related().filter(utente=req.user.id, tipo = 'manuale').values('idGruppi', 'dataOraInserimento', 'nrTest', 'nrGruppo', 'dataOraInizio', 'secondiRitardo')
    display_test_orario = TestsGroup.objects.select_related().filter(utente=req.user.id, tipo = 'orario').values('idGruppi', 'dataOraInserimento', 'nrTest', 'nrGruppo')
    display_test_programmati = Test.objects.filter(tipo = 'collettivo').values('idTest', 'dataOraInizio')
    display_sfide = TestsGroup.objects.filter(tipo = 'sfida', utente = req.user).values('dataOraInizio', 'idGruppi', 'nrTest')
    display_sfida = []

    for sfida in display_sfide:
        
        if sfida['dataOraInizio'] != None:

            if sfida['dataOraInizio'] < datetime.now() : 

                Test.objects.filter(idTest = sfida['idGruppi']).delete()
            else : 

                display_sfida.append([sfida['dataOraInizio'] , sfida['idGruppi'], sfida['nrTest']])

    print(display_sfida)
    gruppi_programmati = []
    for te in display_test_programmati:
        if te['dataOraInizio'] > datetime.now():
            gruppi_programmati.append([te['idTest'], te['dataOraInizio']])
        else:
            Test.objects.filter(idTest = te['idTest']).delete()
    chart_tests = Test.objects.filter(utente=req.user.id, dataOraFine__isnull=False).order_by('-dataOraInizio')
    chart_tests_json = serialize('json', chart_tests)
    
    gruppi_manuale = []
    gruppi_orario = []
    print(display_test_manuale)
    if len(display_test_manuale) != 0:
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
            print('dd')
            TestsGroup.objects.filter(idGruppi = test['idGruppi']).update(nrGruppo=F('nrGruppo') + count)
            test_manuale_esatto = Test.objects.create(utente = req.user, dataOraInizio = primo_t, secondiRitardo = test['secondiRitardo'], nrGruppo = randint(2,3))
            nrgruppo = TestsGroup.objects.filter(idGruppi = test['idGruppi']).values('nrGruppo','dataOraInizio')[0]
            if test['nrTest'] -  nrgruppo['nrGruppo'] > 0:
                gruppi_manuale.append([test['idGruppi'], test['nrTest'] - nrgruppo['nrGruppo' ], nrgruppo['dataOraInizio'].strftime("%Y-%m-%d %H:%M:%S"),test_manuale_esatto.idTest ])
            else : 
                TestsGroup.objects.filter(idGruppi = test['idGruppi']).delete()
    for t in display_test_orario:
        if t['nrTest'] - t['nrGruppo'] > 0:
            gruppi_orario.append([t['idGruppi'], t['nrTest'] - t['nrGruppo'], t['dataOraInserimento'].strftime("%Y-%m-%d %H:%M:%S")])
    return render(req, 'home/home.html', {'display_sfida': display_sfida, 'gruppi_manuale': gruppi_manuale[::-1], 'chart_tests': chart_tests_json , 'gruppi_orario' : gruppi_orario[::-1], 'gruppi_programmati' : gruppi_programmati[::-1] , 'zero' : 0, 'stelle' : stelle})




@login_required(login_url='login')
def creazioneTest(req):
    testManualeForm = TestManualeForm()
    testOrarioEsattoForm = TestOrarioEsattoForm()
    context = {"creaTestManualeForm": testManualeForm, "creaTestOrarioEsattoForm": testOrarioEsattoForm}
    return render(req, 'test/creazioneTest.html', context)



@login_required(login_url='login')
def Sfida(req):
    user_list = User.objects.exclude(Q(id = req.user.id))
    user_lists = list()
    user_fields_list = [user_lists.append((user.username,user.username)) for user in user_list]

    storico_sfide_fatte = Sfide.objects.filter(utente = req.user)
    storico_sfide_ricevute = Sfide.objects.filter(utenteSfidato = req.user)

    sf_fatte = []
    sf_ric = []

    for el in storico_sfide_fatte:
        if el.vincitore != 'pareggio':
            sf_fatte.append([el.utente, el.utenteSfidato, el.dataOraInserimento, el.vincitore])

    for el1 in storico_sfide_ricevute:
        if el1.vincitore != 'pareggio':
            sf_ric.append([el1.utente, el1.utenteSfidato, el1.dataOraInserimento, el1.vincitore])

    creaTestSfidaOrarioEsattoForm = TestSfidaOrarioEsattoForm()

    creaTestSfidaOrarioEsattoForm.fields['utente'].choices = user_lists

    return render(req, 'sfide/sfide.html', {"creaTestSfidaOrarioEsattoForm": creaTestSfidaOrarioEsattoForm, 'sfide_ricevute' : sf_ric, 'sfide_fatte' : sf_fatte}
)


@login_required(login_url='login')
def testCollettivi(req):
    if req.method == 'POST':

        form = FormTestCollettivi(req.POST)
        mutable_data = MultiValueDict(form.data.lists())
        mutable_data['dataOraInizio'] = utils.reformat_date(mutable_data['dataOraInizio'])
        form = FormTestCollettivi(mutable_data) 

        if form.is_valid():

            nPagine = form.cleaned_data['nPagine']
            dataOraInizio = form.cleaned_data['dataOraInizio']

            test_collettivo = Test.objects.create(utente = req.user , nrGruppo = nPagine, tipo = 'collettivo', dataOraInizio = dataOraInizio)
            
            return redirect('creaTestCollettivo' , pagine = nPagine, idTest = test_collettivo.idTest)
        else: 
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(req, f"Errore: {error}")
            print(form.errors)
           

    ctx = {'form' : FormTestCollettivi()}

    return render(req, 'test/testCollettivi.html', ctx)

@login_required(login_url='login')
def creaTestCollettivo(req, pagine, idTest):

    if req.method == 'POST':
                
        return redirect('home')

    return render(req, 'test/testCollettiviDom.html', {'domande' : range(pagine) , 'pagine' : pagine,'idTest' : idTest})

@login_required(login_url='login')
def creaTestCollettivoDisplay(req, idTest, n):
    if req.method == 'POST':
        
        form = FormDomandaCollettiva(req.POST)
        if form.is_valid():

            domanda = form.cleaned_data['Domanda']
            risposta = form.cleaned_data['Risposta']
            variante = form.cleaned_data['Varianti']
            tipo = form.cleaned_data['tipo']


            domanda_test = Domande.objects.create(corpo = domanda, tipo = tipo, numeroPagine = n)
            variante = Varianti.objects.create(domanda = domanda_test, corpo = variante, rispostaEsatta = risposta)
            test = Test.objects.filter(idTest = idTest)[0]
            print(test)
            Test_Domande_Varianti.objects.create(test = test, domanda = domanda_test, variante = variante)    

            return HttpResponse(domanda+' '+risposta+'  '+ variante)

    return render(req, 'test/displayDomanda.html', {'form' : FormDomandaCollettiva() , 'idTest' : idTest, 'n' : n})

@login_required(login_url='login')
def statistiche(req):

    chart_tests = Test.objects.filter(utente=req.user.id, dataOraFine__isnull=True).order_by('-dataOraInizio')
    print(chart_tests)

    tipiDomande = ['testo','selezione','checkbox', 'stelle']
    nrErrori = Statistiche.objects.filter(utente = req.user).values_list('nrErrori', flat=True)

    print(nrErrori)    
    chart = px.pie( names = tipiDomande, values = nrErrori)

    errori_t = Statistiche.objects.filter(utente = req.user, tipoDomanda = 't').values('nrErrori')[0]['nrErrori']
    errori_s = Statistiche.objects.filter(utente = req.user, tipoDomanda = 's').values('nrErrori')[0]['nrErrori']
    errori_c = Statistiche.objects.filter(utente = req.user, tipoDomanda = 'r').values('nrErrori')[0]['nrErrori']



    return render(req ,'statistiche/statistiche.html', { 'chart': chart.to_html, 'test_incompleti' : len(chart_tests), 'errori_t' : errori_t , 'errori_s' : errori_s, 'errori_c' : errori_c})

@login_required(login_url='login')
def controllo(req):
    
    if req.user.is_staff == False:
        redirect('home')

    utenti_inf = []
    print(req.user.username)
    utenti = User.objects.all()
    for utente in utenti:
        check =Test.objects.filter(utente= utente, dataOraFine__isnull=False).order_by('-dataOraInizio')
        if len(check) <= 100:
            utenti_inf.append([utente, len(check)])


    return render(req, 'utenti/Utenti.html', {'utenti_inf' : utenti_inf})