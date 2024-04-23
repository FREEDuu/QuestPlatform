from django.contrib import messages
from ..forms import TestManualeForm, TestSfidaManualeForm
from django.shortcuts import render, redirect
from django.db import transaction
from ..models import *
from ..utils import utils
from datetime import datetime

def creaTestManualeService(req):
    response = {'success': False, 'message': '', 'context': {}}
    
    if req.method == 'POST':
        form = TestManualeForm(req.POST)
        if form.is_valid():
            numero_test = form.cleaned_data['numeroTest']
            
            try:
                with transaction.atomic():
                    TestsGroup.objects.create(utente=req.user, tipo='manuale', nrTest=numero_test)
                
                response['success'] = True
                response['message'] = 'Test creati con successo.'
                
            except Exception as e:
                response['message'] = f"Errore durante creazione test: {e}"
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"Errore: {error}")
                    
            testManualeForm = TestManualeForm()
            testOrarioEsattoForm = form
            response['message'] = ', '.join(error_messages)
            response['context'] = {"creaTestManualeForm": testManualeForm, "creaTestOrarioEsattoForm": testOrarioEsattoForm}
            
    return response




def TestStartService(idGruppi, idTest, counter):
    response = {'success': False, 'message': '', 'context': {}}
    
    ctx = []
    if Test.objects.filter(idTest = idTest).values('dataOraInizio')[0]['dataOraInizio'] is None:

        Test.objects.filter(idTest = idTest).update(dataOraInizio = datetime.now())

    
    ultimo = False
    if Test.objects.filter(idTest = idTest).values('nrGruppo')[0]['nrGruppo'] -1 <= counter:
        ultimo = True
    test_to_render = Test_Domande_Varianti.objects.filter(test = idTest).prefetch_related('domanda','variante').order_by('id')
    
    for domanda in test_to_render:
        
        var_to_app = utils.Create_other_var([])
        ctx.append([domanda.domanda, var_to_app, domanda.variante])
    
    counter += 1
    ctx = ctx[(counter-1)*5:((counter)*5)]
    
    response['success'] = True
    response['context'] = {'ctx' : ctx,'idGruppi' : idGruppi,'idTest' : idTest, 'ultimo': ultimo, 'counter' : counter}
    