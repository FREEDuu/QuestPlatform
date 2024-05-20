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
    print("Errori: ", req.session.get('Errori'))
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
    print("Errori: ", req.session.get('Errori'))

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
    if end_data[1]:  # if malusF5 is True
        malus = True
        tempo_end += 5  # Add 5 seconds
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


def preTestSfida(req, idGruppi, id):

    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('dataOraInizio', 'nrTest')
    
    if(datetime.now() < tests[0]['dataOraInizio']):
        return render(req, 'preTestOrario/preTestOrario.html', {'time_display' : tests[0]['dataOraInizio'].strftime("%Y-%m-%d %H:%M:%S")})
    else:
        singolo_test = Test.objects.create(utente = req.user, tipo = 'sfida', dataOraInizio = datetime.now(), nrGruppo = 3)
        domande = Domande.objects.filter(numeroPagine = -1).exclude(Q(tipo='cr') | Q(attivo=False))
    
        random.seed(id)
        app_list = list()
        choice = random.sample(range(0, len(domande)), 16)


        # Associa domande casuali con la relativa variante casuale al nuovo test creato
        for _ in range(14):
            
            random_domanda = choice[_]
            
            
            varianti = Varianti.objects.filter(domanda = domande[random_domanda])

            app_list.append(Test_Domande_Varianti(test = singolo_test, domanda = domande[random_domanda], variante = varianti[randint(0, len(varianti)-1)]))
            
        domande_cr = Domande.objects.filter(tipo='cr', attivo=True)
        random_domanda_cr = randint(0, len(domande_cr)-1)
        varianti_cr = Varianti.objects.filter(domanda = domande_cr[random_domanda_cr])
        random_variante_cr = randint(0, len(varianti_cr)-1)
    
        domanda_test_cr = Test_Domande_Varianti(test = singolo_test, domanda = domande_cr[random_domanda_cr], variante = varianti_cr[random_variante_cr])

        if randint(0, 1) == 0:
            app_list.insert(0,domanda_test_cr)
        else:
            app_list.append(domanda_test_cr)

        Test_Domande_Varianti.objects.bulk_create(app_list)
        Test.objects.filter(idTest = singolo_test.idTest).update(nrTest = tests[0]['nrTest'])
        return redirect('testStartOrarioSfida', idTest = singolo_test.idTest , displayer = 0)
    

def testStartOrarioSfida(req, idTest, displayer):

    test_to_render = Test_Domande_Varianti.objects.filter(test=idTest).select_related('domanda', 'variante').order_by('id')
    test = Test.objects.filter(idTest=idTest).values('nrGruppo', 'dataOraInizio', 'inSequenza').first()

    domande_to_render = [d.domanda.tipo for d in test_to_render]
    risposte_esatte = [d.variante.rispostaEsatta for d in test_to_render]

    ctx = []
    if req.method == 'POST':
        Test.objects.filter(idTest = idTest).update(inSequenza = False) 
        formRisposta = FormDomanda(domande_to_render, risposte_esatte, req.POST)
        check = False

        # VALIDAZIONE RISPOSTE
        for n in range(displayer * 5, (displayer + 1) * 5):

            if domande_to_render[n] == 'm': 
                concat_string = ''
                for i in range(len(risposte_esatte[n])):
                    user_input = req.POST.get('domanda_{}_{}'.format(n, i))
                    concat_string = ''.join([concat_string, user_input])
                    
                    if user_input != risposte_esatte[n][i]: 
                        formRisposta.fields['domanda_{}'.format(n)].widget.widgets[i].attrs.update({'style': 'width: 38px; margin-right: 10px; border: 1px solid red;'})
                
                if concat_string != test_to_render[n].variante.rispostaEsatta:
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], True, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])
                    check = True
                    Test.objects.filter(idTest = idTest).update(numeroErrori=F('numeroErrori') + 1)
                    Statistiche.objects.filter(utente = req.user, tipoDomanda = 'm').update(nrErrori=F('nrErrori') + 1)
                else:
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

            elif domande_to_render[n] == 'cr':
                if req.POST.get('domanda_{}'.format(n)) != '1':
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], True, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])
                    check = True
                    Test.objects.filter(idTest = idTest).update(numeroErrori=F('numeroErrori') + 1)             
                    Statistiche.objects.filter(utente = req.user, tipoDomanda = formRisposta['domanda_{}'.format(n)].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)
                else:
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

            elif req.POST.get('domanda_{}'.format(n)) != test_to_render[n].variante.rispostaEsatta:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], True, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])
                check = True
                Test.objects.filter(idTest = idTest).update(numeroErrori=F('numeroErrori') + 1)
                Statistiche.objects.filter(utente = req.user, tipoDomanda = formRisposta['domanda_{}'.format(n)].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)

            else:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])



        if check:
            for n in range(displayer * 5, (displayer + 1) * 5):
                if domande_to_render[n] == 'cr':
                    formRisposta.fields['domanda_{}'.format(n)].choices = utils.genRandomStaticAnswers('cr', test_to_render[n].variante.rispostaEsatta)
                else:
                    formRisposta.fields['domanda_{}'.format(n)].choices, seed = utils.genRandomFromSeed(domande_to_render[n], idTest, test_to_render[n].variante.rispostaEsatta)
                    
            return render(req, 'preTestOrario/TestSelectSfida.html', { 'ultimo': test['nrGruppo'], 'idTest': idTest, 'displayer': displayer, 'ctx': ctx})
        
        else:
            if test['nrGruppo'] -1 == displayer:
                return redirect('FinishTestOrarioSfida', idTest = idTest)
            displayer += 1
            ctx = []
            for n in range(displayer * 5, (displayer + 1) * 5):
                if domande_to_render[n] == 'cr':
                    formRisposta.fields['domanda_{}'.format(n)].choices = utils.genRandomStaticAnswers('cr', test_to_render[n].variante.rispostaEsatta)
                else:
                    formRisposta.fields['domanda_{}'.format(n)].choices, seed = utils.genRandomFromSeed(domande_to_render[n], idTest, test_to_render[n].variante.rispostaEsatta)
                
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

            
            return render(req, 'preTestOrario/TestSelectSfida.html', {'ultimo': test['nrGruppo'], 'idTest': idTest, 'displayer': displayer, 'ctx': ctx })

    else:
        if test['inSequenza'] == True:
            Test.objects.filter(idTest = idTest).update(malusF5 = True)
        Test.objects.filter(idTest = idTest).update(inSequenza = True) 
        forms = FormDomanda(domande_to_render, risposte_esatte)
        
        for n in range(len(test_to_render)):
            if n >= displayer * 5 and n < (displayer + 1) * 5:
                if domande_to_render[n] == 'cr':
                    forms.fields['domanda_{}'.format(n)].choices = utils.genRandomStaticAnswers('cr', test_to_render[n].variante.rispostaEsatta)
                else:
                    forms.fields['domanda_{}'.format(n)].choices, seed = utils.genRandomFromSeed(domande_to_render[n], idTest, test_to_render[n].variante.rispostaEsatta)
                
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, forms['domanda_{}'.format(n)], False,'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

        return render(req,'preTestOrario/TestSelectSfida.html', {'ultimo': test['nrGruppo'] -1,'idTest': idTest,'displayer': displayer,'ctx': ctx})
    
    
    
    
def FinishTestOrarioSfida(req, idTest):
        
    end =  Test.objects.filter(idTest = idTest).values('dataOraInizio','dataOraFine', 'nrTest', 'malusF5')[0]
    if end['dataOraFine'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraFine = datetime.now())
    end =  Test.objects.filter(idTest = idTest).values('dataOraInizio','dataOraFine', 'nrTest', 'malusF5')[0]
    malus = False
    tt = Test.objects.filter(idTest = idTest)
    tempo_test_finale = tt[0].dataOraFine
    tempo_test_iniziale = tt[0].dataOraInizio

    sfida = Sfide.objects.filter(idSfida = end['nrTest']).values('dataOraInizio', 'utente', 'utenteSfidato')[0]
    print(sfida)
    tempo_end = (tempo_test_finale-tempo_test_iniziale).total_seconds()
 
    if sfida['dataOraInizio'] == None : 
        Sfide.objects.filter(idSfida = end['nrTest']).update(dataOraInizio = end['dataOraFine'], vincitore = req.user.username)
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
    