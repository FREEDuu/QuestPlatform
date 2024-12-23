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
import random
from django.db.models import Prefetch

def get_domande(req):

    dom = Domande.objects.filter()
    var = Varianti.objects.filter()

    return HttpResponse(var)

def make_domande(req, CorpoDomanda, tipo, VariantiCorpo, VariantiRisposta):

    try:

        Domanda_Generata = Domande.objects.create(corpo = CorpoDomanda, tipo = tipo)
        Varianti_to_generate = VariantiCorpo.split(', ')
        Risposte_varianti = VariantiRisposta.split(', ')

        Varianti_to_push = list()

        for _ in range(len(Varianti_to_generate)):
            Varianti_to_push.append(Varianti(domanda = Domanda_Generata, corpo = Varianti_to_generate[_], rispostaEsatta = Risposte_varianti[_]))
        Varianti.objects.bulk_create(Varianti_to_push)

        return HttpResponse('202 OK')
    
    except Exception as e:
        return HttpResponse(e)

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
    utils.pulisci_sessione(req)
    media = queries.get_user_mean(req.user.id)
    results = queries.get_single_users_tests_week_and_mean(req.user.id)
    is_collettivi_nascosti = queries.get_is_collettivi_nascosti()
    
    if results:
        conteggio_test_settimanali = results[0][0]  
    else:
        conteggio_test_settimanali = 0 
    
    tempo_ref = queries.media_delle_medie()[0][0]
    staff = True    
    if req.user.is_staff == False:
        staff = False
    user_utente = req.user.username
    if '.' in user_utente:
        user_utente = user_utente.split('.')[0]
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
    
    # Conteggio test fatti questa settimana
    weekly_test_count = queries.get_weekly_test_count(req.user.id)[0][0]
    
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
    return render(req, 'home/home.html', { 'tempo_ref' : tempo_ref, 'media' : media, 'conteggio_test_settimanali': conteggio_test_settimanali,'user_utente': user_utente, 'staff':staff, 'is_collettivi_nascosti': is_collettivi_nascosti, 'display_sfida_accettate': display_sfida_accettate, 'display_sfida_attesa_1' : display_sfida_attesa_1,'display_sfida_attesa_2' : display_sfida_attesa_2, 'gruppi_manuale': gruppi_manuale[::-1], 'chart_tests': chart_tests_json , 'gruppi_orario' : gruppi_orario[::-1], 'gruppi_programmati' : gruppi_programmati[::-1] , 'zero' : 0, 'stelle' : stelle, 'weekly_test_count': weekly_test_count})

@login_required(login_url='login')
def setVisibilitaCollettivi(req):
    is_collettivi_nascosti = req.POST.get('is_collettivi_nascosti', None)
    queries.set_is_collettivi_nascosti(is_collettivi_nascosti)
    return redirect('home')

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
    [user_lists.append((user.username,user.username)) for user in user_list]

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
            Test_Domande_Varianti.objects.create(test = test, domanda = domanda_test, variante = varianti, nrPagina = n)    

            return HttpResponse(domanda+' '+risposta+'  '+ str(varianti))

    return render(req, 'test/displayDomanda.html', {'form' : FormDomandaCollettiva() , 'idTest' : idTest, 'n' : n})


@login_required(login_url='login')
def statistiche(req):
    tipiDomande = ['testo', 'selezione', 'checkbox', 'input multiplo']
    tipo_to_label = {'t': 'testo', 's': 'selezione', 'c': 'checkbox', 'm': 'input multiplo'}
    
    nrErrori_raw = queries.get_numero_errori(req.user.id)
    error_dict = {tipo: 0 for tipo in tipiDomande}  # Inizializza con valori a zero

    for count, tipo in nrErrori_raw:
        if tipo in tipo_to_label:
            error_dict[tipo_to_label[tipo]] = count

    nrErrori = [error_dict[tipo] for tipo in tipiDomande]

    chart = px.pie(names=tipiDomande, values=nrErrori)

    errori_t = queries.get_errori_per_tipo(req.user.id, 't')
    errori_s = queries.get_errori_per_tipo(req.user.id, 's')
    errori_c = queries.get_errori_per_tipo(req.user.id, 'c')
    errori_cr = queries.get_errori_per_tipo(req.user.id, 'cr')
    errori_m = queries.get_errori_per_tipo(req.user.id, 'm')
    
    test_incompleti = queries.get_test_incompleti(req.user.id)

    return render(req, 'statistiche/statistiche.html', {
        'chart': chart.to_html(),
        'test_incompleti': len(test_incompleti),
        'errori_t': errori_t,
        'errori_s': errori_s,
        'errori_c': errori_c,
        'errori_cr': errori_c,
        'errori_m': errori_m
    })


#@login_required(login_url='login')
def controllo(req):
    if req.user.is_staff == False:
        return redirect('home')
    
    result_set = queries.get_user_test_info()
    columns = ['username', 'idTest', 'dataOraInizio', 'dataOraFine', 'nrGruppo', 'nrDomande', 'numeroErrori', 'malusF5']
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
        
        # calcola totale secondi
        duration_seconds = (el['dataOraFine'] - el['dataOraInizio']).total_seconds() if el['dataOraFine'] and el['dataOraInizio'] else 0

        arr_display.append([
            el['username'],
            el['idTest'],
            dataOraFine_str,
            dataOraInizio_str,
            el['nrGruppo'],
            el['nrDomande'],
            el['numeroErrori'],
            el['malusF5'],
            duration_seconds
        ])


    # Conteggio test utenti questa settimana
    utenti_inf = queries.get_users_tests_week_and_mean()

    # Dati stelle utenti
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

    # Estrazione dati test
    result_set = queries.get_user_test_info()
    columns = ['username', 'idTest', 'dataOraInizio', 'dataOraFine', 'nrGruppo', 'nrDomande', 'numeroErrori', 'malusF5']
    tutti_test = [dict(zip(columns, row)) for row in result_set]
    
    # Titoli colonne header del CSV
    header_row = ['Utente', 'ID Test', 'Data Inizio', 'Data Fine', 'Nr Pagine', 'Nr Domande', 'Nr Errori', 'Penalty refresh', 'Tempo Completamento']
    writer.writerow(header_row)
    
    for test in tutti_test:
        tempo_completamento = (test['dataOraFine'] - test['dataOraInizio']).total_seconds()
        tempo_completamento_str = str(tempo_completamento).replace('.', ',')

        writer.writerow([
            test['username'],
            test['idTest'],
            test['dataOraInizio'].strftime("%d/%m/%Y %H:%M:%S"),
            test['dataOraFine'].strftime("%d/%m/%Y %H:%M:%S"),
            test['nrGruppo'],
            test['nrDomande'],
            test['numeroErrori'],
            test['malusF5'],
            tempo_completamento_str
        ])

    csv_content = csv_buffer.getvalue()

    csv_buffer.close()

    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
 

@login_required(login_url='login')
def csv_riepilogo_ultimo_collettivo(req):
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"risultati_collettivo_{current_date}.csv"
    csv_buffer = StringIO()
    
    writer = csv.writer(csv_buffer, delimiter=';')

    # Estrazione dati ultimo test collettivo
    check_collettivo = queries.check_collettivo_available()
    
    if check_collettivo == 0:
        return redirect('controllo')
        
    result_set = queries.get_risultati_collettivo()
    columns = ['username', 'dataOraInizio', 'dataOraFine', 'duration_seconds']
    tutti_test = [dict(zip(columns, row)) for row in result_set]
    
    # Titoli colonne header del CSV
    header_row = ['Utente', 'Data Inizio', 'Data Fine', 'Tempo']
    writer.writerow(header_row)
    
    for test in tutti_test:
        tempo_completamento = (test['dataOraFine'] - test['dataOraInizio']).total_seconds()
        tempo_completamento_str = str(tempo_completamento).replace('.', ',')

        writer.writerow([
            test['username'],
            test['dataOraInizio'].strftime("%d/%m/%Y %H:%M:%S"),
            test['dataOraFine'].strftime("%d/%m/%Y %H:%M:%S"),
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


def RiepilogoTest(req, idGruppi, idTest, counter, seed):
    test_compilato = Test_Domande_Varianti.objects.filter(test=idTest).select_related('domanda', 'variante')

    num_items = len(test_compilato)

    if num_items >= 6:
        scelte = random.sample(range(num_items), 6)
    else:
        scelte = list(range(num_items))

    random.seed(datetime.now().second)
    randomico = random.randint(0, 2)

    context = []
    for scelta in scelte:
        selected_item = test_compilato[scelta]
        context.append([selected_item.domanda.corpo + ' ' + selected_item.variante.corpo, selected_item.variante.rispostaEsatta])

    return render(req, 'RiepilogoTest/RiepilogoTest.html', {
        'idGruppi': idGruppi,
        'idTest': idTest,
        'ctx': context,
        'counter': counter,
        'random': randomico,
        'seed': seed,
        'idTestSfida': seed
    })



def esciDalTest(req):
    queries.insert_nuova_statistica(req.user.id, 'esci')
    queries.update_incrementa_statistica(req.user.id, 'esci')
    
    return redirect('home')



# Gestione Domande
@login_required(login_url='login')
def gestione_domande(req):
    if req.method == 'POST' and req.headers.get('X-Requested-With') == 'XMLHttpRequest':
        domanda_id = req.POST.get('domanda_id')
        action = req.POST.get('action')
        domanda = Domande.objects.get(idDomanda=domanda_id)
        domanda.attivo = True if action == 'activate' else False
        domanda.save()
        return JsonResponse({'status': 'success'})

    domande = Domande.objects.prefetch_related(
        Prefetch('varianti_set', queryset=Varianti.objects.all())
    )
    return render(req, 'gestioneDomande/gestioneDomande.html', {'domande': domande})


@login_required(login_url='login')
def get_varianti(req, domanda_id):
    varianti = Varianti.objects.filter(domanda_id=domanda_id).values('idVariante', 'corpo', 'rispostaEsatta')
    return JsonResponse({'varianti': list(varianti)})


@login_required(login_url='login')
def add_variante(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            domanda_id = request.POST.get('domanda_id')
            corpo = request.POST.get('corpo')
            risposta_esatta = request.POST.get('risposta_esatta')
            
            domanda = Domande.objects.get(idDomanda=domanda_id)
            variante = Varianti.objects.create(
                domanda=domanda,
                corpo=corpo,
                rispostaEsatta=risposta_esatta
            )
            
            return JsonResponse({
                'status': 'success',
                'variante': {
                    'idVariante': variante.idVariante,
                    'corpo': variante.corpo,
                    'rispostaEsatta': variante.rispostaEsatta
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required(login_url='login')
def delete_variante(request, variante_id):
    if (request.method in ['DELETE', 'POST']) and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            variante = Varianti.objects.get(idVariante=variante_id)
            variante.delete()
            return JsonResponse({'status': 'success'})
        except Varianti.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Variante non trovata'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@login_required(login_url='login')
def update_domanda(request, domanda_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            domanda = Domande.objects.get(idDomanda=domanda_id)
            domanda.corpo = request.POST.get('corpo')
            domanda.save()
            return JsonResponse({
                'status': 'success',
                'domanda': {
                    'corpo': domanda.corpo
                }
            })
        except Domande.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Domanda non trovata'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)