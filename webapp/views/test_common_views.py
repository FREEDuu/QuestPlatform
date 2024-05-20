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

    ultimo = False
    if queries.get_nr_gruppo(idTest) - 1 <= counter:
        ultimo = True

    test_to_render = queries.get_test_domande_varianti(idTest)
    test = queries.get_test_data(idTest)
    
    dom_to_r = []
    var_to_r = []
    domande_to_render = []
    risposte_esatte = []
    for d in test_to_render:
        if d.numeroPagine == counter:
            domande_to_render.append(d.tipo)
            risposte_esatte.append(d.rispostaEsatta) 
            dom_to_r.append(d.corpoDomanda)
            var_to_r.append(d)   
            
    if req.method == 'POST':
        formRisposta = FormDomanda(domande_to_render, risposte_esatte, req.POST)
        ctx, corrected_errors = utils.Validazione(req, formRisposta, domande_to_render, idTest, test_to_render, risposte_esatte, counter)

        if corrected_errors:
            return render(req, 'preTest/TestSelectProgrammati.html', {
                'ultimo': ultimo,
                'idTest': idTest,
                'counter': counter,
                'ctx': ctx
            })
        else:
            if test['nrGruppo'] - 1 == counter:
                return redirect('TestProgrammatiFinish', idTest=idTest)
                        
            test_to_render = queries.get_test_domande_varianti(idTest)
            test = queries.get_test_data(idTest)
            
            counter += 1
            domande_to_render = []
            dom_to_r = []
            var_to_r = []
            risposte_esatte = []
            for d in test_to_render:
                if d.numeroPagine == counter:
                    domande_to_render.append(d.tipo)
                    dom_to_r.append(d.corpoDomanda)
                    risposte_esatte.append(d.rispostaEsatta)  
                    var_to_r.append(d)
            ctx = []
            formRisposta = FormDomanda(domande_to_render, risposte_esatte)
            
            for n in range(len(domande_to_render)):
                formRisposta.fields[f'domanda_{n}'].choices = genRandomFromSeedCollettivi(var_to_r[n].corpoVariante, var_to_r[n].rispostaEsatta)
                ctx.append([dom_to_r[n], var_to_r[n].corpoVariante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', domande_to_render[n]])

            return render(req, 'preTest/TestSelectProgrammati.html', {
                'ultimo': ultimo,
                'idTest': idTest,
                'counter': counter,
                'ctx': ctx
            })
    else:
        formRisposta = FormDomanda(domande_to_render, risposte_esatte)

        form_data = req.session.get(page_key, None)

        if not form_data:
            for n in range(len(domande_to_render)):
                formRisposta.fields[f'domanda_{n}'].choices = genRandomFromSeedCollettivi(var_to_r[n].corpoVariante, var_to_r[n].rispostaEsatta)
                ctx.append([dom_to_r[n], var_to_r[n].corpoVariante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', domande_to_render[n]])
        else:
            # Pre-populate the form with data from the session for the current page
            ctx = utils.repopulate_form(formRisposta, form_data, test_to_render, risposte_esatte, counter, req.session.get('Errori'))

            if req.session.get('Errori') and req.session.get('Errori')[0]['pagina'] == counter:
                del req.session['Errori']

        return render(req, 'preTest/TestSelectProgrammati.html', {
            'ultimo': ultimo,
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
    print(test_finito)

    if len(test_finito) == 0:
        
        tests = Test.objects.filter(idTest = idTest).values('dataOraInizio', 'secondiRitardo')[0]

        test_finito = Test.objects.create(utente = req.user, dataOraInizio = tests['dataOraInizio'] , dataOraFine = datetime.now(), tipo = 'collettivo_finito_' + str(idTest))
    else :
        test_finito = Test.objects.filter(utente = req.user, tipo = 'collettivo_finito_' + str(idTest))[0]

    tempo_test_finale = test_finito.dataOraFine.second
    tempo_test_iniziale = test_finito.dataOraInizio.second

    if tempo_test_finale < tempo_test_iniziale:
        tempo_finish = tempo_test_finale +60  - tempo_test_iniziale
    else:
        tempo_finish = tempo_test_finale - tempo_test_iniziale
    
    utils.pulisci_sessione(req)

    return render(req, 'preTest/FinishTestProgrammati.html', {'tempo' : tempo_finish})

    