from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.db.models import F
from webapp.models import Test 
from django.contrib.auth import authenticate, login, logout 
from ..forms import LoginForm, TestManualeForm, TestOrarioEsattoForm, TestSfidaManualeForm, TestSfidaOrarioEsattoForm, FormTestCollettivi, FormDomandaCollettiva, FormDomandaCollettivaCrea
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
from django.views.decorators.csrf import csrf_exempt
import csv
from io import StringIO
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.urls import reverse
from time import perf_counter
from django.db import connection
from django.http import JsonResponse
import json
from ..utils import queries

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

def rifiutaSfida(req, idGruppi, id):
    Sfide.objects.filter(idSfida = id).delete()
    TestsGroup.objects.filter(nrTest = id).delete()
    return redirect('home')

def accettaSfida(req,idGruppi,id):

    TestsGroup.objects.filter(nrTest = id).update(tipo = 'sfida_accettata')

    return redirect('home')

# HOME
@login_required(login_url='login')
def home(req):
    staff = True    
    if req.user.is_staff == False:
        staff = False

    if len(Statistiche.objects.filter(utente = req.user, tipoDomanda = 'stelle')) == 0:
        Statistiche.objects.create(utente = req.user, tipoDomanda = 'stelle', nrErrori = 0)
        Statistiche.objects.create(utente = req.user, tipoDomanda = 't', nrErrori = 0)
        Statistiche.objects.create(utente = req.user, tipoDomanda = 's', nrErrori = 0)
        Statistiche.objects.create(utente = req.user, tipoDomanda = 'r', nrErrori = 0)

    stelle = Statistiche.objects.filter(utente = req.user, tipoDomanda = 'stelle')[0].nrErrori

    display_test_manuale = TestsGroup.objects.select_related().filter(utente=req.user.id, tipo = 'manuale').values('idGruppi', 'dataOraInserimento', 'nrTest', 'nrGruppo', 'dataOraInizio', 'secondiRitardo')
    display_test_orario = TestsGroup.objects.select_related().filter(utente=req.user.id, tipo = 'orario').values('idGruppi', 'dataOraInserimento', 'nrTest', 'nrGruppo')
    display_test_programmati = Test.objects.filter(tipo = 'collettivo').values('idTest', 'dataOraInizio')
    display_sfide_attesa_1 = TestsGroup.objects.filter(tipo = 'sfida_attesa_1', utente = req.user).values('dataOraInizio', 'idGruppi', 'nrTest','tipo')
    display_sfide_attesa_2 = TestsGroup.objects.filter(tipo = 'sfida_attesa_2', utente = req.user).values('dataOraInizio', 'idGruppi', 'nrTest', 'tipo')
    display_sfide_accettate = TestsGroup.objects.filter(tipo = 'sfida_accettata', utente = req.user).values('dataOraInizio', 'idGruppi', 'nrTest')
    display_sfida_attesa_1 = []
    display_sfida_attesa_2 = []
    display_sfida_accettate = []
    
    for sfida in display_sfide_attesa_1:

        utente = Sfide.objects.filter(idSfida = sfida['nrTest'])[0]
        
        if sfida['dataOraInizio'] != None:

            if sfida['dataOraInizio'] < datetime.now() : 

                TestsGroup.objects.filter(nrTest = sfida['nrTest']).delete()

            else : 
                display_sfida_attesa_1.append([sfida['dataOraInizio'] , sfida['idGruppi'], utente.utenteSfidato, sfida['nrTest']])
                
    for sfida2 in display_sfide_attesa_2:

        utente = Sfide.objects.filter(idSfida = sfida2['nrTest'])[0]

        if sfida2['dataOraInizio'] != None:

            if sfida2['dataOraInizio'] < datetime.now() : 

                TestsGroup.objects.filter(nrTest = sfida2['nrTest']).delete()
            else : 
                display_sfida_attesa_2.append([sfida2['dataOraInizio'] , sfida2['idGruppi'], utente.utente, sfida2['nrTest']])
                
    for sfida3 in display_sfide_accettate:

        utente = Sfide.objects.filter(idSfida = sfida3['nrTest'])[0]

        if utente.utente == req.user:
            
            utente = utente.utenteSfidato

        else:

            utente = utente.utente

        if sfida3['dataOraInizio'] != None:

            if sfida3['dataOraInizio'] < datetime.now() : 

                TestsGroup.objects.filter(nrTest = sfida3['nrTest']).delete()
            else : 
                display_sfida_accettate.append([sfida3['dataOraInizio'] , sfida3['idGruppi'], utente, sfida3['nrTest']])

    gruppi_programmati = []
    for te in display_test_programmati:
        if te['dataOraInizio'] > datetime.now():
            gruppi_programmati.append([te['idTest'], te['dataOraInizio']])
    chart_tests = Test.objects.filter(utente=req.user.id, dataOraFine__isnull=False).order_by('dataOraInizio')
    chart_tests_json = serialize('json', chart_tests)
    
    gruppi_manuale = []
    gruppi_orario = []
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
    return render(req, 'home/home.html', {'staff':staff, 'display_sfida_accettate': display_sfida_accettate, 'display_sfida_attesa_1' : display_sfida_attesa_1,'display_sfida_attesa_2' : display_sfida_attesa_2, 'gruppi_manuale': gruppi_manuale[::-1], 'chart_tests': chart_tests_json , 'gruppi_orario' : gruppi_orario[::-1], 'gruppi_programmati' : gruppi_programmati[::-1] , 'zero' : 0, 'stelle' : stelle})




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
            sf_fatte.append([el.utente, el.utenteSfidato, el.dataOraInizio, el.vincitore])

    for el1 in storico_sfide_ricevute:
        if el1.vincitore != 'pareggio':
            sf_ric.append([el1.utente, el1.utenteSfidato, el1.dataOraInizio, el1.vincitore])

    # Ordina per data discendente
    sf_fatte.sort(key=lambda x: x[2], reverse=True)
    sf_ric.sort(key=lambda x: x[2], reverse=True)

    creaTestSfidaOrarioEsattoForm = TestSfidaOrarioEsattoForm()

    creaTestSfidaOrarioEsattoForm.fields['utente'].choices = user_lists

    return render(req, 'sfide/sfide.html', {"creaTestSfidaOrarioEsattoForm": creaTestSfidaOrarioEsattoForm, 'sfide_ricevute' : sf_ric[:5], 'sfide_fatte' : sf_fatte[:5]}
)


@login_required(login_url='login')
def testCollettivi(req):


    if req.user.is_staff == False:
        return redirect('home')

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

@csrf_exempt
@login_required(login_url='login')
def creaTestCollettivoDisplay(req, idTest, n):
    if req.method == 'POST':
        
        form = FormDomandaCollettiva(req.POST)
        if form.is_valid():

            domanda = form.cleaned_data['Domanda']
            risposta = form.cleaned_data['Risposta']
            varianti = form.cleaned_data['Varianti']
            tipo = form.cleaned_data['tipo']


            domanda_test = Domande.objects.create(corpo = domanda, tipo = tipo, numeroPagine = n)
            varianti = Varianti.objects.create(domanda = domanda_test, corpo = varianti, rispostaEsatta = risposta)
            test = Test.objects.filter(idTest = idTest)[0]
            print(test)
            Test_Domande_Varianti.objects.create(test = test, domanda = domanda_test, variante = varianti)    

            return HttpResponse(domanda+' '+risposta+'  '+ str(varianti))

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

#@login_required(login_url='login')
def controllo(req):
    if req.user.is_staff == False:
        return redirect('home')
    
    result_set = queries.get_user_test_info()
    columns = ['username', 'idTest', 'dataOraFine', 'dataOraInizio', 'nrGruppo', 'nrTest', 'numeroErrori', 'malusF5']
    tests = [dict(zip(columns, row)) for row in result_set]

    # Paginazione
    paginator = Paginator(tests, 10)
    page_number = req.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    arr_display = []
    for el in page_obj:
        # Formatta date
        dataOraFine_str = el['dataOraFine'].strftime("%d/%m/%Y %H:%M:%S") if el['dataOraFine'] else ''
        dataOraInizio_str = el['dataOraInizio'].strftime("%d/%m/%Y %H:%M:%S") if el['dataOraInizio'] else ''
        
        # Calcula totale secondi
        duration_seconds = (el['dataOraFine'] - el['dataOraInizio']).total_seconds() if el['dataOraFine'] and el['dataOraInizio'] else 0

        arr_display.append([
            el['username'],
            el['idTest'],
            dataOraFine_str,
            dataOraInizio_str,
            el['nrGruppo'],
            el['nrTest'],
            el['numeroErrori'],
            el['malusF5'],
            duration_seconds
        ])


    # Fetch users with fewer than 100 tests this week
    utenti_inf = queries.get_users_tests_100()

    utenti_stelle = queries.get_stelle_statistics()

    # Render response based on HTMX request or not
    if req.headers.get('HX-Request'):
        template_name = 'utenti/tabellaRiepilogoTest.html'
        context = {'page_obj': page_obj, 'arr_display': arr_display}
    else:
        template_name = 'utenti/Utenti.html'
        context = {'utenti_inf': utenti_inf, 'utenti_stelle': utenti_stelle, 'page_obj': page_obj, 'arr_display': arr_display}

    return TemplateResponse(req, template_name, context)



@login_required(login_url='login')
def csv_riepilogo_test(req):
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"data_{current_date}.csv"

    csv_buffer = StringIO()
    
    writer = csv.writer(csv_buffer, delimiter=';')

    header_row = ['Utente', 'ID Test', 'Data Inizio', 'Data Fine', 'Nr Pagine', 'Nr Domande', 'Nr Errori', 'Malus F5', 'Tempo Completamento']
    writer.writerow(header_row)

    tutti_test = Test.objects.select_related('utente').filter(dataOraFine__isnull=False).exclude(Q(tipo="sfida") | Q(tipo__startswith="collettivo")).order_by('-dataOraInizio')
    
    for test in tutti_test:
        tempo_completamento = (test.dataOraFine - test.dataOraInizio).total_seconds()
        tempo_completamento_str = str(tempo_completamento).replace('.', ',')

        writer.writerow([
            test.utente.username,
            test.idTest,
            test.dataOraInizio.strftime("%d/%m/%Y %H:%M:%S"),
            test.dataOraFine.strftime("%d/%m/%Y %H:%M:%S"),
            test.nrGruppo,
            test.nrTest,
            test.numeroErrori,
            test.malusF5,
            tempo_completamento_str
        ])

    csv_content = csv_buffer.getvalue()

    csv_buffer.close()

    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
 

def creaDomande(req):

    if req.user.is_staff == False:
        return redirect('home')
    

    
    return render(req, 'creaDomande/creaDomande.html')

def creaDomandeDisplay(req):
    
    if req.method == 'POST':
        
        form = FormDomandaCollettiva(req.POST)
        if form.is_valid():

            domanda = form.cleaned_data['Domanda']
            risposte = form.cleaned_data['Risposta']
            risposte = risposte.split(';')
            varianti = form.cleaned_data['Varianti']
            varianti = varianti.split(';')
            tipo = form.cleaned_data['tipo']

            domanda = Domande.objects.create(corpo = domanda, tipo = tipo, numeroPagine = -1)
            to_list = list()
            for _ in range(len(risposte)):
                to_list.append(Varianti(domanda = domanda, corpo = varianti[_], rispostaEsatta = risposte[_]))
            Varianti.objects.bulk_create(to_list)
            print(to_list, domanda)

            return HttpResponse('variante creata')

    return render(req, 'creaDomande/displayDom.html', {'form' : FormDomandaCollettiva()})