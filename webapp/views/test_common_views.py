from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from ..models import *
from . import page_views
from datetime import datetime
from django.db.models import F

from ..forms import *

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

def TestProgrammatiStart(req, idTest, counter):

    ctx = []
    
    ultimo = False
    if Test.objects.filter(idTest = idTest).values('nrGruppo')[0]['nrGruppo'] - 1 <= counter:
        ultimo = True

    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).select_related('domanda','variante')
    test = Test.objects.filter(idTest=idTest).values('nrGruppo', 'dataOraInizio').first()
    
        #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

    domande_to_render = []
    risposte_esatte = []
    for d in test_to_render:
        if d.domanda.numeroPagine == counter:
            domande_to_render.append(d.domanda.tipo)
            risposte_esatte.append(d.variante.rispostaEsatta)    
    
    print(domande_to_render)
    if req.method == 'POST':

        formRisposta = FormDomanda(domande_to_render,risposte_esatte, req.POST)
        check = False
        for n in range(len(domande_to_render)):
            if req.POST.get('domanda_{}'.format(n)) != test_to_render[n].variante.rispostaEsatta:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], True, 'domanda_{}'.format(n)])

                Statistiche.objects.filter(utente = req.user, tipoDomanda = formRisposta['domanda_{}'.format(n)].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)
                check = True
            else:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False, 'domanda_{}'.format(n)])

        if check:
            for n in range(len(domande_to_render)):
                pass
                #formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
            return render(req, 'preTest/TestSelectProgrammati.html', {'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx})
        else:
            if test['nrGruppo'] -1 == counter:
                return redirect('FinishTestProgrammati', idTest = idTest)
            
            test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).select_related('domanda','variante')
            test = Test.objects.filter(idTest=idTest).values('nrGruppo', 'dataOraInizio').first()
            
                #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))

            domande_to_render = []
            risposte_esatte = []
            for d in test_to_render:
                if d.domanda.numeroPagine == counter:
                    domande_to_render.append(d.domanda.tipo)
                    risposte_esatte.append(d.variante.rispostaEsatta)   
            counter += 1
            ctx = []
            forms = FormDomanda(domande_to_render, risposte_esatte)

            for n in range(len(domande_to_render)):
                #formRisposta.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n)])

            
            return render(req, 'preTest/TestSelectProgrammati.html', {'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx})

    else:
        forms = FormDomanda(domande_to_render, risposte_esatte)
        
        for n in range(len(domande_to_render)):
            
            #forms.fields['domanda_{}'.format(n)].choices, seed = genRandomFromSeed(seed, test_to_render[n].variante.rispostaEsatta)
            ctx.append([test_to_render[n].domanda, test_to_render[n].variante, forms['domanda_{}'.format(n)], False,'domanda_{}'.format(n)])

        return render(req, 'preTest/TestSelectProgrammati.html', {'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx})

def TestProgrammatiFinish(req, idTest):
        
    tests = TestsGroup.objects.filter(idGruppi = idGruppi).values('dataOraInizio', 'secondiRitardo')[0]

    test_finito = Test.objects.filter(idTest = idTest).values('dataOraInizio', 'secondiRitardo')[0]
    id_next_test = Test.objects.create(utente = req.user, dataOraInizio = test_finito['dataOraInizio'] + timedelta(0, tests['secondiRitardo']), nrGruppo = randint(2,3))
    TestsGroup.objects.filter(idGruppi = idGruppi).update(dataOraInizio = id_next_test.dataOraInizio)
    end =  Test.objects.filter(idTest = idTest).values('dataOraFine')[0]
    if end['dataOraFine'] is None:
        Test.objects.filter(idTest = idTest).update(dataOraFine = datetime.now())
    tt = Test.objects.filter(idTest = idTest)
    tempo_test_finale = tt[0].dataOraFine.second
    tempo_test_iniziale = tt[0].dataOraInizio.second

    if tempo_test_finale < tempo_test_iniziale:
            tempo_finish = tempo_test_finale +60  - tempo_test_iniziale
    else:
        tempo_finish = tempo_test_finale - tempo_test_iniziale

    return render(req, 'preTest/FinishTest.html', {'idGruppi' : idGruppi ,'tempo' : tempo_finish, 'idTest' : id_next_test.idTest })

    