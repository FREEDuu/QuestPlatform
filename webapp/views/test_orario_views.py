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
from django.db.models.query import QuerySet
from django import forms 


def genRandomFromSeed(seed, rispostaGiusta):
    random.seed(seed)
    ret = [('1',str(randint(0,9))),('2',str(randint(0,8))),(str(rispostaGiusta), str(rispostaGiusta))]
    random.shuffle(ret)
    return ret , seed+1

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

    TestsGroup.objects.filter(idGruppi = idGruppi).update(nrGruppo=F('nrGruppo') + 1)
    singolo_test = Test.objects.create(utente = req.user, nrGruppo = randint(2,3))
    domande = Domande.objects.prefetch_related()

    app_list = list()

    for _ in range(15):

        random_domanda = randint(0, len(domande)-1)
        varianti = Varianti.objects.filter(domanda = domande[random_domanda])

        app_list.append(Test_Domande_Varianti(test = singolo_test, domanda = domande[random_domanda], variante = varianti[randint(0, len(varianti)-1)]))
        
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
            TestsGroup.objects.filter(idGruppi = idGruppi).update(dataOraInizio = None)
            return redirect('testStartOrario', idGruppi = idGruppi, idTest=idTest, counter = counter, displayer = 0, seed = randint(0,1000))
    else:
        return test_common_views.cancella_un_test(req, idGruppi)


def testStartOrario(req, idGruppi, idTest, counter, displayer, seed):

    test_to_render = Test_Domande_Varianti.objects.filter(test=idTest).select_related('domanda', 'variante')
    test = Test.objects.filter(idTest=idTest).values('nrGruppo', 'dataOraInizio').first()

    domande_to_render = [d.domanda.tipo for d in test_to_render]
    risposte_esatte = [d.variante.rispostaEsatta for d in test_to_render]
    
    ctx = []
    if req.method == 'POST':
        print(displayer, test['nrGruppo'] )
        formRisposta = FormDomanda(domande_to_render, risposte_esatte, req.POST)
        check = False

        for n in range(displayer * 5, (displayer + 1) * 5):
            if req.POST.get('domanda_{}'.format(n)) != test_to_render[n].variante.rispostaEsatta:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], True, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])
                check = True
                if isinstance(formRisposta['domanda_{}'.format(n)].field.widget, forms.MultiWidget):
                    tipo_domanda = test_to_render[n].domanda.tipo
                    Statistiche.objects.filter(utente=req.user, tipoDomanda=tipo_domanda).update(nrErrori=F('nrErrori') + 1)
                else:
                    tipo_domanda = formRisposta['domanda_{}'.format(n)].field.widget.input_type[0]
                    Statistiche.objects.filter(utente=req.user, tipoDomanda=tipo_domanda).update(nrErrori=F('nrErrori') + 1)

            else:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

        if check:
            for n in range(displayer * 5, (displayer + 1) * 5):
                formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
            return render(req, 'preTestOrario/TestSelect.html', {'idGruppi': idGruppi, 'ultimo': test['nrGruppo'], 'idTest': idTest, 'counter': counter, 'displayer': displayer, 'ctx': ctx, 'seed': seed})
        else:
            if test['nrGruppo'] -1 == displayer:
                return redirect('FinishTestOrario', idGruppi = idGruppi, idTest = idTest, counter = counter)
            displayer += 1
            ctx = []
            for n in range(displayer * 5, (displayer + 1) * 5):
                formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

            
            return render(req, 'preTestOrario/TestSelect.html', {'idGruppi': idGruppi, 'ultimo': test['nrGruppo'], 'idTest': idTest, 'counter': counter, 'displayer': displayer, 'ctx': ctx , 'seed': seed})

    else:
        formRisposta = FormDomanda(domande_to_render, risposte_esatte)

        for n in range(len(test_to_render)):
            if n >= displayer * 5 and n < (displayer + 1) * 5:
                formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n), test_to_render[n].domanda.tipo])

        return render(req,'preTestOrario/TestSelect.html', {'idGruppi': idGruppi,'ultimo': test['nrGruppo'] -1,'idTest': idTest,'counter': counter,'displayer': displayer,'ctx': ctx,'seed': seed})



def FinishTestOrario(req, idGruppi, idTest, counter):
        
    counter += 1
    end =  Test.objects.filter(idTest = idTest).values('dataOraFine')[0]
    if end['dataOraFine'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraFine = datetime.now())
    
    tt = Test.objects.filter(idTest = idTest)
    tempo_test_finale = tt[0].dataOraFine
    tempo_test_iniziale = tt[0].dataOraInizio


    return render(req, 'preTestOrario/FinishTest.html', {'idGruppi' : idGruppi ,'tempo' : (tempo_test_finale-tempo_test_iniziale).total_seconds() , 'counter' : counter})





##### SFIDA #####

@login_required(login_url='login')
def creaTestSfidaOrarioEsatto(req):
    
    if req.method == 'POST':

        dataorainizio = req.POST['dataOraInizio']
        dataorainizio  = datetime.strptime(dataorainizio, '%d-%m-%Y %H:%M')
        utente = User.objects.filter(username = req.POST['utente'])[0]

        id_sfida = randint(0,100000)

        if dataorainizio > datetime.now():
            
            TestsGroup.objects.create(utente = req.user, dataOraInizio = dataorainizio, tipo = 'sfida', nrGruppo = 3, nrTest = id_sfida)
            TestsGroup.objects.create(utente = utente, dataOraInizio = dataorainizio, tipo = 'sfida', nrGruppo = 3, nrTest = id_sfida)

        
        else : 
           return redirect('Sfida')
    return redirect('/home')


def preTestSfida(req, idGruppi, id):

    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('dataOraInizio')
    
    if(datetime.now() < tests[0]['dataOraInizio']):
        return render(req, 'preTestOrario/preTestOrario.html', {'time_display' : tests[0]['dataOraInizio'].strftime("%Y-%m-%d %H:%M:%S")})
    else:
        singolo_test = Test.objects.create(utente = req.user, tipo = 'sfida', dataOraInizio = datetime.now(), nrGruppo = 3)
        domande = Domande.objects.select_related()
    
        random.seed(id)
        app_list = list()

                # Associa domande casuali con la relativa variante casuale al nuovo test creato
        for _ in range(15):

            random_domanda = randint(0, len(domande)-1)
            print(random_domanda)
            varianti = Varianti.objects.filter(domanda = domande[random_domanda])

            app_list.append(Test_Domande_Varianti(test = singolo_test, domanda = domande[random_domanda], variante = varianti[randint(0, len(varianti)-1)]))
            
        Test_Domande_Varianti.objects.bulk_create(app_list)

        return redirect('testStartOrarioSfida', idTest = singolo_test.idTest , displayer = 0)
    

def testStartOrarioSfida(req, idTest, displayer):

    test_to_render = Test_Domande_Varianti.objects.filter(test=idTest).select_related('domanda', 'variante')
    test = Test.objects.filter(idTest=idTest).values('nrGruppo', 'dataOraInizio').first()

    domande_to_render = [d.domanda.tipo for d in test_to_render]
    risposte_esatte = [d.variante.rispostaEsatta for d in test_to_render]

    ctx = []
    if req.method == 'POST':
        formRisposta = FormDomanda(domande_to_render, risposte_esatte, req.POST)
        check = False

        for n in range(displayer * 5, (displayer + 1) * 5):
            if req.POST.get('domanda_{}'.format(n)) != test_to_render[n].variante.rispostaEsatta:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], True, 'domanda_{}'.format(n)])
                check = True
                print(formRisposta['domanda_{}'.format(n)].field.widget.input_type[0])
                Statistiche.objects.filter(utente = req.user, tipoDomanda = formRisposta['domanda_{}'.format(n)].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)

            else:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n)])

        if check:
            for n in range(displayer * 5, (displayer + 1) * 5):
                formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(idTest, test_to_render[n].variante.rispostaEsatta)
            return render(req, 'preTestOrario/TestSelectSfida.html', { 'ultimo': test['nrGruppo'], 'idTest': idTest, 'displayer': displayer, 'ctx': ctx})
        else:
            if test['nrGruppo'] -1 == displayer:
                return redirect('FinishTestOrarioSfida', idTest = idTest)
            displayer += 1
            ctx = []
            for n in range(displayer * 5, (displayer + 1) * 5):
                formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(idTest, test_to_render[n].variante.rispostaEsatta)
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n)])

            
            return render(req, 'preTestOrario/TestSelectSfida.html', {'ultimo': test['nrGruppo'], 'idTest': idTest, 'displayer': displayer, 'ctx': ctx })

    else:
        forms = FormDomanda(domande_to_render, risposte_esatte)
        
        for n in range(len(test_to_render)):
            if n >= displayer * 5 and n < (displayer + 1) * 5:
                forms.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(idTest, test_to_render[n].variante.rispostaEsatta)
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, forms['domanda_{}'.format(n)], False,'domanda_{}'.format(n)])

        return render(req,'preTestOrario/TestSelectSfida.html', {'ultimo': test['nrGruppo'] -1,'idTest': idTest,'displayer': displayer,'ctx': ctx})
    
def FinishTestOrarioSfida(req, idTest):
        
    end =  Test.objects.filter(idTest = idTest).values('dataOraFine')[0]
    if end['dataOraFine'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraFine = datetime.now())
    
    tt = Test.objects.filter(idTest = idTest)
    tempo_test_finale = tt[0].dataOraFine
    tempo_test_iniziale = tt[0].dataOraInizio


    return render(req, 'preTestOrario/FinishTestSfida.html', {'tempo' : (tempo_test_finale-tempo_test_iniziale).total_seconds()})
    