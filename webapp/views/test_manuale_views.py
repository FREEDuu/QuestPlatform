from __future__ import unicode_literals
from datetime import datetime
from django.db.models import F
from django.shortcuts import render, redirect
from webapp.models import Domande, Varianti, Test, Test_Domande_Varianti
from ..forms import TestManualeForm, TestSfidaManualeForm, FormDomanda
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from ..models import *
from random import randint
from . import test_common_views
from ..utils import utils
from django.utils.datastructures import MultiValueDict
from datetime import datetime, timedelta
from . import test_common_views
from ..utils.utils import genRandomStaticAnswers
import random
import string


def genRandomint(num):
    if randint(0,1) == 0:
        return randint(0, num-1)
    else: 
        return randint(num+1, 9)
def randomGen(lungh, to_repl):
    ret = random.choices(string.ascii_lowercase, k=lungh)
    while ret == to_repl:
       ret = random.choices(string.ascii_lowercase, k=lungh)
    
    return ret[0]
def genRandomFromSeed(tipo, seed, rispostaGiusta):
    if True :
        if tipo == 's':
            app_list = list()
            app_list.append(('', '- selezionare opzione -'))
            
            if len(rispostaGiusta) == 1 and str(rispostaGiusta).isdigit() :
                for _ in range(0, randint(6,14)):
                    num = int(rispostaGiusta)
                    var = genRandomint(num)
                    app_list.append((str(_), str(var)))
                app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
                ret = app_list
            else:
                for _ in range(0, randint(6,14)):
                    var = str(rispostaGiusta)
                    to_repl = var[randint(0,len(var)-1)]
                    var  = var.replace(to_repl, randomGen(1, to_repl))
                    if str(var) != str(rispostaGiusta):
                        app_list.append((str(_), var))
                app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
                ret = app_list
            
        else:
            app_list = list()

            if len(rispostaGiusta) == 1 and str(rispostaGiusta).isdigit() :
                for _ in range(0, randint(6,14)):
                    num = int(rispostaGiusta)
                    var = genRandomint(num)
                    app_list.append((str(_), str(var)))
                app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
                ret = app_list
            else:
                for _ in range(0, randint(6,14)):
                    var = str(rispostaGiusta)
                    to_repl = var[randint(0,len(var)-1)]
                    var  = var.replace(to_repl, randomGen(1, to_repl))
                    if str(var) != str(rispostaGiusta):
                            app_list.append((str(_), var))
                app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
                ret = app_list
    # Per le select mescolare tutto tranne il primo valore di default
    if tipo == 's':
        shuffled_options = ret[1:]
        random.shuffle(shuffled_options)
        ret[1:] = shuffled_options
    else:
        random.shuffle(ret)
    return ret , seed


@login_required(login_url='login')
def creaTestManuale(req):
    if req.method == 'POST':
        form = TestManualeForm(req.POST)
        mutable_data = MultiValueDict(form.data.lists())
        mutable_data['dataOraInizio'] = utils.reformat_date(mutable_data['dataOraInizio'])
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
def TestStart(req, idGruppi, idTest, counter, seed):

    ctx = []
    random.seed(seed)
    ultimo = False
    if Test.objects.filter(idTest = idTest).values('nrGruppo')[0]['nrGruppo'] - 1 <= counter:
        ultimo = True
    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).select_related('domanda','variante')
    test = Test.objects.filter(idTest=idTest).values('nrGruppo', 'dataOraInizio', 'inSequenza').first()
    
        #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

    domande_to_render = [d.domanda.tipo for d in test_to_render]
    risposte_esatte = [d.variante.rispostaEsatta for d in test_to_render]

    if req.method == 'POST':
        Test.objects.filter(idTest = idTest).update(inSequenza = False)

        formRisposta = FormDomanda(domande_to_render,risposte_esatte, req.POST)
        check = False
        
        # VALIDAZIONE RISPOSTE
        for n in range(counter * 5, (counter + 1) * 5):
            
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
                    Statistiche.objects.filter(utente = req.user, tipoDomanda = 'm').update(nrErrori=F('nrErrori') + 1)
                    Test.objects.filter(idTest = idTest).update(numeroErrori=F('numeroErrori') + 1)
                else:
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

            elif domande_to_render[n] == 'cr':
                if req.POST.get('domanda_{}'.format(n)) != '1':
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], True, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])
                    check = True
                    Statistiche.objects.filter(utente = req.user, tipoDomanda = formRisposta['domanda_{}'.format(n)].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)
                    Test.objects.filter(idTest = idTest).update(numeroErrori=F('numeroErrori') + 1)

                else:
                    ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

            elif req.POST.get('domanda_{}'.format(n)) != test_to_render[n].variante.rispostaEsatta:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], True, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])
                check = True
                Statistiche.objects.filter(utente = req.user, tipoDomanda = formRisposta['domanda_{}'.format(n)].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)
                Test.objects.filter(idTest = idTest).update(numeroErrori=F('numeroErrori') + 1)


            else:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])


        if check:
            for n in range(counter * 5, (counter + 1) * 5):
                if domande_to_render[n] == 'cr':
                    formRisposta.fields['domanda_{}'.format(n)].choices = genRandomStaticAnswers('cr', test_to_render[n].variante.rispostaEsatta)
                else:
                    formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(domande_to_render[n], seed, test_to_render[n].variante.rispostaEsatta)
                
            return render(req, 'preTest/TestSelect.html', {'idGruppi': idGruppi, 'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx, 'seed': seed, })
        else:
            if test['nrGruppo'] -1 == counter:
                return redirect('FinishTest', idGruppi = idGruppi, idTest = idTest)
            counter += 1
            ctx = []
            for n in range(counter * 5, (counter + 1) * 5):
                if domande_to_render[n] == 'cr':
                    formRisposta.fields['domanda_{}'.format(n)].choices = genRandomStaticAnswers('cr', test_to_render[n].variante.rispostaEsatta)
                else:
                    formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(domande_to_render[n], seed, test_to_render[n].variante.rispostaEsatta)

                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

            
            return render(req, 'preTest/TestSelect.html', {'idGruppi': idGruppi, 'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx, 'seed': seed+1})

    else:
        if test['inSequenza'] == True:
            Test.objects.filter(idTest = idTest).update(malusF5 = True)
            print('MALUS F5')
        Test.objects.filter(idTest = idTest).update(inSequenza = True) 
        forms = FormDomanda(domande_to_render, risposte_esatte)
        
        for n in range(counter * 5, (counter + 1) * 5):
            
            if domande_to_render[n] == 'cr':
                forms.fields['domanda_{}'.format(n)].choices = genRandomStaticAnswers('cr', test_to_render[n].variante.rispostaEsatta)
            else:
                forms.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(domande_to_render[n], seed, test_to_render[n].variante.rispostaEsatta)
            
            ctx.append([test_to_render[n].domanda, test_to_render[n].variante, forms['domanda_{}'.format(n)], False,'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

        return render(req, 'preTest/TestSelect.html', {'idGruppi': idGruppi, 'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx, 'seed': seed})


def preTest(req, idGruppi, idTest):

    singolo_test =  Test.objects.filter(idTest = idTest)[0]

    if datetime.now() > singolo_test.dataOraInizio:
        
        TestsGroup.objects.filter(idGruppi = idGruppi).update(nrGruppo=F('nrGruppo') + 1)
        tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('nrTest' , 'inSequenza', 'secondiRitardo', 'dataOraInizio', 'nrGruppo')
        nrTest = tests[0]['nrTest'] - tests[0]['nrGruppo']
        
        if(nrTest >= 0):
            
            domande = Domande.objects.filter(numeroPagine = -1).exclude(tipo='cr')
            choice = random.sample(range(0, len(domande)), 16)
            app_list = list()

            # Associa domande casuali con la relativa variante casuale al nuovo test creato
            for _ in range(14):

                random_domanda = choice[_]

                varianti = Varianti.objects.filter(domanda = domande[random_domanda])

                app_list.append(Test_Domande_Varianti(test = singolo_test, domanda = domande[random_domanda], variante = varianti[randint(0, len(varianti)-1)]))
        
            domande_cr = Domande.objects.filter(tipo='cr')
            random_domanda_cr = randint(0, len(domande_cr)-1)
            varianti_cr = Varianti.objects.filter(domanda = domande_cr[random_domanda_cr])
            random_variante_cr = randint(0, len(varianti_cr)-1)
            
            domanda_test_cr = Test_Domande_Varianti(test = singolo_test, domanda = domande_cr[random_domanda_cr], variante = varianti_cr[random_variante_cr])
            
            if randint(0, 1) == 0:
                app_list.insert(0,domanda_test_cr)
            else:
                app_list.append(domanda_test_cr)

            Test_Domande_Varianti.objects.bulk_create(app_list)

            return redirect('TestStart' , idGruppi = idGruppi, idTest = idTest, counter = 0, seed = randint(0,1000))

        else :

            return test_common_views.cancella_un_test(req, idGruppi)
    else : 
        
        return render(req, 'preTest/preTest.html', {'time_display' : singolo_test.dataOraInizio.strftime("%Y-%m-%d %H:%M:%S")})



def FinishTest(req, idGruppi, idTest):
        
    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('dataOraInizio', 'secondiRitardo')[0]

    test_finito = Test.objects.filter(idTest = idTest).values('dataOraInizio', 'secondiRitardo')[0]
    id_next_test = Test.objects.create(utente = req.user, dataOraInizio = test_finito['dataOraInizio'] + timedelta(0, tests['secondiRitardo']), nrGruppo = randint(2,3))
    TestsGroup.objects.filter(idGruppi = idGruppi).update(dataOraInizio = id_next_test.dataOraInizio)
    end =  Test.objects.filter(idTest = idTest).values('dataOraFine', 'malusF5')[0]
    if end['dataOraFine'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraFine = datetime.now())
    tt = Test.objects.filter(idTest = idTest)
    tempo_test_finale = tt[0].dataOraFine
    tempo_test_iniziale = tt[0].dataOraInizio
    tempo_end = (tempo_test_finale-tempo_test_iniziale).total_seconds

    if end['malusF5'] == True:
        malus = True
        tempo_end = (tempo_test_finale-tempo_test_iniziale + timedelta(0,  5)).total_seconds
        Test.objects.filter(idTest = idTest).update(dataOraFine = tempo_test_finale + timedelta(0,5))

    return render(req, 'preTest/FinishTest.html', {'idGruppi' : idGruppi ,'tempo' : tempo_end, 'idTest' : id_next_test.idTest , 'malus' : malus})


##### SFIDA #####
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