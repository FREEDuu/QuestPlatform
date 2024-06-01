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
from ..utils import utils
from django.urls import reverse
from django.db.models import Q
from ..utils import queries

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
    queries.update_tests_group_nrGruppo(idGruppi)
    singolo_test = queries.create_new_test(req.user.id)

    domande = queries.get_filtered_domande()
    random.shuffle(domande)

    domanda_ids = [d[0] for d in domande]
    varianti = queries.get_varianti_for_domande(domanda_ids)
    varianti_dict = {domanda_id: [] for domanda_id in domanda_ids}
    for var in varianti:
        varianti_dict[var[1]].append(var)
    
    for p in range(singolo_test['nrGruppo']):
        for _ in range(random.randint(2, 4)):
            if not domande:
                break

            random_domanda = domande.pop()
            random_domanda_id = random_domanda[0]
            if random_domanda_id in varianti_dict:
                varianti = varianti_dict[random_domanda_id]
                if varianti:
                    random_variante = random.choice(varianti)
                    queries.bulk_create_test_domande_varianti(
                        test_id=singolo_test['idTest'],
                        domanda_id=random_domanda_id,
                        variante_id=random_variante[0],
                        nrPagina=p
                    )
        
        if random.randint(0, 1) == 1:
            domande_cr = queries.get_filtered_domande_cr()
            if domande_cr:
                random_domanda_cr = random.choice(domande_cr)
                varianti_cr = queries.get_varianti_for_domande([random_domanda_cr[0]])
                if varianti_cr:
                    random_variante_cr = random.choice(varianti_cr)
                    queries.bulk_create_test_domande_varianti(
                        test_id=singolo_test['idTest'],
                        domanda_id=random_domanda_cr[0],
                        variante_id=random_variante_cr[0],
                        nrPagina=p
                    )

    return redirect('preTestOrario', idGruppi=idGruppi, idTest=singolo_test['idTest'], counter=counter)


@login_required(login_url='login')
def preTestOrario(req, idGruppi, idTest, counter):
    tests = queries.get_tests_group_details(idGruppi)
    test = queries.get_test_details(idTest)

    if test['dataOraInizio'] is None:
        new_time = datetime.now() + timedelta(seconds=tests['secondiRitardo'])
        queries.update_test_dataOraInizio(idTest, new_time)
        return preTestOrario(req, idGruppi, idTest, counter)

    nrTest = tests['nrTest'] - tests['nrGruppo']
    random.seed(idTest)
    if random.randint(0, 1) == 1:
        variazione_randomica = test['dataOraInizio'] - timedelta(seconds=1)
    else:
        variazione_randomica = test['dataOraInizio'] + timedelta(seconds=1)

    if nrTest >= 0:
        if datetime.now() < variazione_randomica:
            return render(req, 'preTestOrario/preTestOrario.html', {'time_display': test['dataOraInizio'].strftime("%Y-%m-%d %H:%M:%S")})
        else:
            queries.update_testsgroup_dataOraInizio(idGruppi, None)
            return redirect('testStartOrario', idGruppi=idGruppi, idTest=idTest, counter=counter, displayer=0, seed=random.randint(0, 1000))
    else:
        return test_common_views.cancella_un_test(req, idGruppi)


@login_required(login_url='login')
def testStartOrario(req, idGruppi, idTest, counter, displayer, seed):
    #print("Errori: ", req.session.get('Errori'))
    page_key = f'form_data_page_{displayer}'

    test_to_render = queries.get_test_to_render(idTest, displayer)
    test = queries.get_test_details(idTest)

    domande_to_render = [row.tipo for row in test_to_render]
    risposte_esatte = [row.rispostaEsatta for row in test_to_render]
    random.seed(seed)
    formRisposta = FormDomanda(domande_to_render, risposte_esatte)

    utils.generaOpzioniRisposta(formRisposta, test_to_render, seed)

    if req.method == 'POST':
        ctx, corrected_errors = utils.Validazione(req, formRisposta, domande_to_render, idTest, test_to_render, risposte_esatte, displayer)
        
        # Store form data in the session by page
        req.session[page_key] = req.POST
        req.session.save()

        # Remove corrected errors from the session
        if req.session.get('Errori'):
            req.session['Errori'] = [error for error in req.session.get('Errori', []) if error not in corrected_errors]
            req.session.save() 

        if test['nrGruppo'] - 1 <= displayer:
            if random.randint(0, 1) == 1:
                return redirect('FinishTestOrario', idGruppi=idGruppi, idTest=idTest, counter=counter, seed=seed)
            else:
                return redirect('RiepilogoTest', idGruppi=idGruppi, idTest=idTest, counter=counter, seed=seed)

        displayer += 1
        return redirect(reverse('testStartOrario', kwargs={
            'idGruppi': idGruppi,
            'idTest': idTest,
            'counter': counter,
            'displayer': displayer,
            'seed': seed
        }))

    else:
        # Pre-populate the form with data from the session for the current page
        form_data = req.session.get(page_key, None)

        if not form_data:
            ctx = [(row.corpoDomanda, row.corpoVariante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', row.tipo) for n, row in enumerate(test_to_render)]
        else:
            ctx = utils.repopulate_form(formRisposta, form_data, test_to_render, risposte_esatte, displayer, req.session.get('Errori'))

            if req.session.get('Errori') and req.session.get('Errori')[0]['pagina'] == displayer:
                del req.session['Errori']

    return render(req, 'GenericTest/GenericTestSelect.html', {
        'random': randint(0, 2),
        'idGruppi': idGruppi,
        'ultimo': test['nrGruppo'] - 1,
        'idTest': idTest,
        'counter': counter,
        'displayer': displayer,
        'ctx': ctx,
        'seed': seed
    })

   

@login_required(login_url='login')
def FinishTestOrario(req, idGruppi, idTest, counter, seed):

    if req.session.get('Errori'):
        primo_errore = req.session['Errori'][0]
        displayer = primo_errore['pagina']

        return redirect(reverse('testStartOrario', kwargs={
            'idGruppi': idGruppi,
            'idTest': idTest,
            'counter': counter,
            'displayer': displayer,
            'seed': seed
        }))

    # Pulisci sessione se il test è concluso senza errori
    utils.pulisci_sessione(req)

    counter += 1
    end_data = queries.get_test_end_data(idTest)
    malus = False

    if end_data[0] is None:
        queries.update_test_end_time(idTest)

    test_times = queries.get_test_times(idTest)
    tempo_test_finale = test_times[0]
    tempo_test_iniziale = test_times[1]
    tempo_end = (tempo_test_finale - tempo_test_iniziale).total_seconds()
    if end_data[1]: 
        malus = True
        tempo_end += 5 
        tempo_test_finale = queries.update_test_end_time_with_malus(idTest, tempo_test_finale)

    return render(req, 'preTestOrario/FinishTest.html', {
        'idGruppi': idGruppi,
        'tempo': tempo_end,
        'counter': counter,
        'malus': malus
    })









##### SFIDA #####

@login_required(login_url='login')
def creaTestSfidaOrarioEsatto(req):
    
    if req.method == 'POST':

        dataorainizio = req.POST['dataOraInizio']
        dataorainizio  = datetime.strptime(dataorainizio, '%d-%m-%Y %H:%M')
        utente = User.objects.filter(username = req.POST['utente'])[0]


        if dataorainizio > datetime.now():

            sfida = Sfide.objects.create(utente = req.user, utenteSfidato = utente)
            TestsGroup.objects.create(utente = req.user, dataOraInizio = dataorainizio, tipo = 'sfida_attesa_1', nrGruppo = 3, nrTest = sfida.idSfida)
            TestsGroup.objects.create(utente = utente, dataOraInizio = dataorainizio, tipo = 'sfida_attesa_2', nrGruppo = 3, nrTest = sfida.idSfida)

        else : 
           return redirect('Sfida')
    return redirect('/home')


def preTestSfida(req, idGruppi, idTestSfida):
    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('dataOraInizio', 'nrTest')

    if(datetime.now() < tests[0]['dataOraInizio']):
        return render(req, 'preTestOrario/preTestOrario.html', {'time_display' : tests[0]['dataOraInizio'].strftime("%Y-%m-%d %H:%M:%S")})
    else:


        domande = queries.get_filtered_domande()
        random.seed(idTestSfida)
        random.shuffle(domande)
        
        nrGruppo = random.randint(2, 3)

        singolo_test = queries.create_new_test_sfida(req.user.id, nrGruppo)
        queries.update_test_dataOraInizio(singolo_test['idTest'], datetime.now())

        domanda_ids = [d[0] for d in domande]
        varianti = queries.get_varianti_for_domande(domanda_ids)
        varianti_dict = {domanda_id: [] for domanda_id in domanda_ids}
        for var in varianti:
            varianti_dict[var[1]].append(var)
        
        for p in range(singolo_test['nrGruppo']):
            for _ in range(random.randint(2, 4)):
                if not domande:
                    break

                random_domanda = domande.pop()
                random_domanda_id = random_domanda[0]
                if random_domanda_id in varianti_dict:
                    varianti = varianti_dict[random_domanda_id]
                    if varianti:
                        random_variante = random.choice(varianti)
                        queries.bulk_create_test_domande_varianti(
                            test_id=singolo_test['idTest'],
                            domanda_id=random_domanda_id,
                            variante_id=random_variante[0],
                            nrPagina=p
                        )
            
            if random.randint(0, 1) == 1:
                domande_cr = queries.get_filtered_domande_cr()
                if domande_cr:
                    random_domanda_cr = random.choice(domande_cr)
                    varianti_cr = queries.get_varianti_for_domande([random_domanda_cr[0]])
                    if varianti_cr:
                        random_variante_cr = random.choice(varianti_cr)
                        queries.bulk_create_test_domande_varianti(
                            test_id=singolo_test['idTest'],
                            domanda_id=random_domanda_cr[0],
                            variante_id=random_variante_cr[0],
                            nrPagina=p
                        )
        return redirect('testStartOrarioSfida', idTest = singolo_test['idTest'] , displayer = 0, idTestSfida = idTestSfida)
    

def testStartOrarioSfida(req, idTest, displayer, idTestSfida):
    page_key = f'form_data_page_{displayer}'

    test_to_render = queries.get_test_to_render(idTest, displayer)
    test = queries.get_test_details(idTest)

    domande_to_render = [row.tipo for row in test_to_render]
    risposte_esatte = [row.rispostaEsatta for row in test_to_render]
    formRisposta = FormDomanda(domande_to_render, risposte_esatte)

    utils.generaOpzioniRisposta(formRisposta, test_to_render, idTestSfida)

    ctx = []
    if req.method == 'POST':
        ctx, corrected_errors = utils.Validazione(req, formRisposta, domande_to_render, idTest, test_to_render, risposte_esatte, displayer)
        
        # Store form data in the session by page
        req.session[page_key] = req.POST
        req.session.save()

        # Remove corrected errors from the session
        if req.session.get('Errori'):
            req.session['Errori'] = [error for error in req.session.get('Errori', []) if error not in corrected_errors]
            req.session.save() 

        if test['nrGruppo'] - 1 <= displayer:
            return redirect('RiepilogoTest', idGruppi=1, idTest=idTest, counter=displayer, seed=idTestSfida)

        displayer += 1
        return redirect(reverse('testStartOrarioSfida', kwargs={
            'idTest': idTest,
            'displayer': displayer,
            'idTestSfida': idTestSfida
        }))

    else:
        # Pre-populate the form with data from the session for the current page
        form_data = req.session.get(page_key, None)

        if not form_data:
            ctx = [(row.corpoDomanda, row.corpoVariante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', row.tipo) for n, row in enumerate(test_to_render)]
        else:
            ctx = utils.repopulate_form(formRisposta, form_data, test_to_render, risposte_esatte, displayer, req.session.get('Errori'))

            if req.session.get('Errori') and req.session.get('Errori')[0]['pagina'] == displayer:
                del req.session['Errori']

    return render(req,'preTestOrario/TestSelectSfida.html', {
        'ultimo': test['nrGruppo'] -1,
        'idTest': idTest,
        'displayer': displayer,
        'idTestSfida': idTestSfida,
        'ctx': ctx
        })
    
    
    
    
def FinishTestOrarioSfida(req, idTest, idTestSfida):
    
    if req.session.get('Errori'):
        primo_errore = req.session['Errori'][0]
        displayer = primo_errore['pagina']

        return redirect(reverse('testStartOrarioSfida', kwargs={
            'idTest': idTest,
            'displayer': displayer,
            'idTestSfida': idTestSfida
        }))

    # Pulisci sessione se il test è concluso senza errori
    utils.pulisci_sessione(req)

        
    end =  Test.objects.filter(idTest = idTest).values('dataOraInizio','dataOraFine', 'nrTest', 'malusF5')[0]
    if end['dataOraFine'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraFine = datetime.now())
    end =  Test.objects.filter(idTest = idTest).values('dataOraInizio','dataOraFine', 'nrTest', 'malusF5')[0]
    malus = False
    tt = Test.objects.filter(idTest = idTest)
    tempo_test_finale = tt[0].dataOraFine
    tempo_test_iniziale = tt[0].dataOraInizio

    sfida = Sfide.objects.filter(idSfida = idTestSfida).values('dataOraInizio', 'utente', 'utenteSfidato')[0]
    tempo_end = (tempo_test_finale-tempo_test_iniziale).total_seconds()
 
    if sfida['dataOraInizio'] == None : 
        Sfide.objects.filter(idSfida = idTestSfida).update(dataOraInizio = end['dataOraFine'], vincitore = req.user.username)
        Statistiche.objects.filter(utente = req.user, tipoDomanda = 'stelle').update(nrErrori=F('nrErrori') + 1)
        if sfida['utente'] == req.user.id:
            Statistiche.objects.filter(utente = sfida['utenteSfidato'] , tipoDomanda = 'stelle').update(nrErrori=F('nrErrori') - 1)
        else:
            Statistiche.objects.filter(utente = sfida['utente'] , tipoDomanda = 'stelle').update(nrErrori=F('nrErrori') - 1)
    if end['malusF5'] == True:
        malus = True
        tempo_end = (tempo_test_finale-tempo_test_iniziale + timedelta(0,  5)).total_seconds()
        Test.objects.filter(idTest = idTest).update(dataOraFine = tempo_test_finale + timedelta(0,5))

    return render(req, 'preTestOrario/FinishTestSfida.html', {'tempo' : tempo_end, 'malus' : malus})
    