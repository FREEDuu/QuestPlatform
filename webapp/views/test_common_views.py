from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from ..models import *
from . import page_views
from datetime import datetime
from django.db.models import F
from ..utils.utils import genRandomStaticAnswers
from ..utils import queries, utils
from django.urls import reverse


from ..forms import *
def genRandomFromSeedCollettivi(varianti, risposta):

    arr = varianti.split(';')
    arr.append( str(risposta))
    ret = list()

    for el in range(len(arr)):

        if arr[el] == str(risposta):
            ret.append((str(risposta), str(risposta)))
        else:
            ret.append((str(el), str(arr[el])))

    return ret    

@login_required(login_url='login')
def delete_all_user_test(req):
    TestsGroup.objects.filter(utente = req.user.id).delete()

    return page_views.home(req) 

def cancella_un_test(req, idGruppi):
    TestsGroup.objects.filter(idGruppi = idGruppi).delete()

    return page_views.home(req)


def TestProgrammati(req, idTest):
    
    singolo_test =  Test.objects.filter(idTest = idTest)[0]

    if datetime.now() > singolo_test.dataOraInizio:
        

        return redirect('TestProgrammatiStart' ,idTest = idTest, counter = 0)
    else : 
        
        return render(req, 'preTest/preTest.html', {'time_display' : singolo_test.dataOraInizio.strftime("%Y-%m-%d %H:%M:%S")})




@login_required(login_url='login')
def TestProgrammatiStart(req, idTest, counter):
    ctx = []
    page_key = f'form_data_page_{counter}'

    test_to_render = queries.get_test_domande_varianti(idTest, counter)
    test = queries.get_test_data(idTest)
    
    tipi_domande_to_render = [row.tipo for row in test_to_render] 
    risposte_esatte = [row.rispostaEsatta for row in test_to_render] 
            
    if req.method == 'POST':
        utils.print_sessione(req)
        formRisposta = FormDomanda(tipi_domande_to_render, risposte_esatte, req.POST)
        ctx, corrected_errors = utils.Validazione(req, formRisposta, tipi_domande_to_render, idTest, test_to_render, risposte_esatte, counter)

        if test['nrGruppo'] - 1 == counter:
            return redirect('RiepilogoTest', idGruppi=0, idTest=idTest, counter=counter, seed=idTest)
                 
        counter += 1   
        return redirect(reverse('TestProgrammatiStart', kwargs={
            'idTest': idTest,
            'counter': counter
        }))
        
    else:
        formRisposta = FormDomanda(tipi_domande_to_render, risposte_esatte)

        form_data = req.session.get(page_key, None)

        utils.print_sessione(req)
        if not form_data:
            for n in range(len(test_to_render)):
                formRisposta.fields[f'domanda_{n}'].choices = genRandomFromSeedCollettivi(test_to_render[n].corpoVariante, test_to_render[n].rispostaEsatta)
                ctx.append([test_to_render[n].corpoDomanda, test_to_render[n].corpoVariante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', tipi_domande_to_render[n]])
        else:
            for n in range(len(test_to_render)):
                formRisposta.fields[f'domanda_{n}'].choices = genRandomFromSeedCollettivi(test_to_render[n].corpoVariante, test_to_render[n].rispostaEsatta)

            # Pre-populate the form with data from the session for the current page
            ctx = utils.repopulate_form(formRisposta, form_data, test_to_render, risposte_esatte, counter, req.session.get('Errori'))

            if req.session.get('Errori') and req.session.get('Errori')[0]['pagina'] == counter:
                del req.session['Errori']

        return render(req, 'preTest/TestSelectProgrammati.html', {
            'idTest': idTest,
            'counter': counter,
            'ctx': ctx
        })


def TestProgrammatiFinish(req, idTest):

    if req.session.get('Errori'):
        primo_errore = req.session['Errori'][0]
        displayer = primo_errore['pagina']

        return redirect(reverse('TestProgrammatiStart', kwargs={
            'idTest': idTest,
            'counter': displayer
        }))
       
       
        
    test_finito = Test.objects.filter(utente = req.user, tipo = 'collettivo_finito_' + str(idTest))

    if len(test_finito) == 0:
        
        tests = Test.objects.filter(idTest = idTest).values('dataOraInizio', 'secondiRitardo')[0]

        test_finito = Test.objects.create(utente = req.user, dataOraInizio = tests['dataOraInizio'] , dataOraFine = datetime.now(), tipo = 'collettivo_finito_' + str(idTest))
    else :
        test_finito = Test.objects.filter(utente = req.user, tipo = 'collettivo_finito_' + str(idTest))[0]

    tempo_test_finale = test_finito.dataOraFine
    tempo_test_iniziale = test_finito.dataOraInizio

    tempo_finish = (tempo_test_finale - tempo_test_iniziale).total_seconds()

    utils.pulisci_sessione(req)

    return render(req, 'preTest/FinishTestProgrammati.html', {'tempo' : tempo_finish})

    