from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from ..models import *
from . import page_views
from datetime import datetime
from django.db.models import F

from ..forms import *
def genRandomFromSeedCollettivi(varianti, risposta):

    arr = varianti.split(' ')
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

def TestProgrammatiStart(req, idTest, counter):
    ctx = []
    
    ultimo = False
    if Test.objects.filter(idTest = idTest).values('nrGruppo')[0]['nrGruppo'] - 1 <= counter:
        ultimo = True

    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).select_related('domanda','variante')
    test = Test.objects.filter(idTest=idTest).values('nrGruppo', 'dataOraInizio').first()
    
        #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))
    dom_to_r = []
    var_to_r = []
    domande_to_render = []
    risposte_esatte = []
    for d in test_to_render:
        if d.domanda.numeroPagine == counter:
            domande_to_render.append(d.domanda.tipo)
            risposte_esatte.append(d.variante.rispostaEsatta) 
            dom_to_r.append(d.domanda.corpo)
            var_to_r.append(d.variante)   
    if req.method == 'POST':

        formRisposta = FormDomanda(domande_to_render,risposte_esatte, req.POST)
        check = False
        for n in range(len(domande_to_render)):
            if req.POST.get('domanda_{}'.format(n)) != var_to_r[n].rispostaEsatta:
                print(req.POST, )
                ctx.append([dom_to_r[n], var_to_r[n].corpo, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n)])
                #Statistiche.objects.filter(utente = req.user, tipoDomanda = formRisposta['domanda_{}'.format(n)].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)
                check = True
            else:
                ctx.append([dom_to_r[n], var_to_r[n].corpo, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n)])
        if check:
            for n in range(len(domande_to_render)):
                formRisposta.fields['domanda_{}'.format(n)].choices = genRandomFromSeedCollettivi(var_to_r[n].corpo, var_to_r[n].rispostaEsatta)
                
            return render(req, 'preTest/TestSelectProgrammati.html', {'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx})
        else:
            if test['nrGruppo'] -1 == counter:
                return redirect('TestProgrammatiFinish', idTest = idTest)
                        
            test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).select_related('domanda','variante')
            test = Test.objects.filter(idTest=idTest).values('nrGruppo', 'dataOraInizio').first()
            
                #Test_Domande_Varianti.objects.create(test=nuovo_test, domanda=Domande.objects.get(idDomanda=idDomandaCasuale), variante=Varianti.objects.get(idVariante=idVarianteCasuale))
            counter += 1
            domande_to_render = []
            dom_to_r = []
            var_to_r = []
            risposte_esatte = []
            for d in test_to_render:
                if d.domanda.numeroPagine == counter:
                    domande_to_render.append(d.domanda.tipo)
                    dom_to_r.append(d.domanda.corpo)
                    risposte_esatte.append(d.variante.rispostaEsatta)  
                    var_to_r.append(d.variante)
            ctx = []
            print(domande_to_render, risposte_esatte)
            formRisposta = FormDomanda(domande_to_render, risposte_esatte)
            print(formRisposta)
            
            for n in range(len(domande_to_render)):
                formRisposta.fields['domanda_{}'.format(n)].choices = genRandomFromSeedCollettivi(var_to_r[n].corpo, var_to_r[n].rispostaEsatta)
                ctx.append([dom_to_r[n], var_to_r[n].corpo, formRisposta['domanda_{}'.format(n)], False,'domanda_{}'.format(n)])

            return render(req, 'preTest/TestSelectProgrammati.html', {'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx})

    else:
        forms = FormDomanda(domande_to_render, risposte_esatte)
        
        for n in range(len(domande_to_render)):
            
            forms.fields['domanda_{}'.format(n)].choices = genRandomFromSeedCollettivi(var_to_r[n].corpo, var_to_r[n].rispostaEsatta)
            ctx.append([dom_to_r[n], var_to_r[n].corpo, forms['domanda_{}'.format(n)], False,'domanda_{}'.format(n)])

        return render(req, 'preTest/TestSelectProgrammati.html', {'ultimo': ultimo, 'idTest': idTest, 'counter': counter,'ctx': ctx})

def TestProgrammatiFinish(req, idTest):

    test_finito = Test.objects.filter(utente = req.user, tipo = 'collettivo_finito_' + str(idTest))
    print(test_finito)

    if len(test_finito) == 0:
        
        tests = Test.objects.filter(idTest = idTest).values('dataOraInizio', 'secondiRitardo')[0]

        test_finito = Test.objects.create(dataOraInizio = tests['dataOraInizio'] , dataOraFine = datetime.now(), tipo = 'collettivo_finito_' + str(idTest))
    else :
        test_finito = Test.objects.filter(utente = req.user, tipo = 'collettivo_finito_' + str(idTest))[0]

    tempo_test_finale = test_finito.dataOraFine.second
    tempo_test_iniziale = test_finito.dataOraInizio.second

    if tempo_test_finale < tempo_test_iniziale:
        tempo_finish = tempo_test_finale +60  - tempo_test_iniziale
    else:
        tempo_finish = tempo_test_finale - tempo_test_iniziale
    

    return render(req, 'preTest/FinishTestProgrammati.html', {'tempo' : tempo_finish})

    