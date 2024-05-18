# utils.py
from django.utils import timezone
from datetime import datetime, date
from random import randint
import random
import string
from django.db.models import F

from webapp.models import Domande, Varianti, Test, Test_Domande_Varianti, Statistiche

### VALIDAZIONE ###
def Validazione(req, formRisposta, domande_to_render, idTest, test_to_render, risposte_esatte, displayer):
    ctx = []
    errors = []
    corrected_errors = []
    form_data = {}

    existing_errors = req.session.get('Errori', [])

    for n in range(len(domande_to_render)):
        if domande_to_render[n] == 'm' and not req.session.get('Trovato', False):
            concat_string = ''
            for i in range(len(risposte_esatte[n])):
                user_input = req.POST.get(f'domanda_{n}_{i}')
                concat_string = ''.join([concat_string, user_input])
                '''

                if user_input != risposte_esatte[n][i]:
                    formRisposta.fields[f'domanda_{n}'].widget.widgets[i].attrs.update({'style': 'width: 38px; margin-right: 10px; border: 1px solid red;'})

                    '''
                # Salva tutti gli input
                form_data[f'domanda_{n}_{i}'] = user_input

            if concat_string != test_to_render[n].variante.rispostaEsatta:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta[f'domanda_{n}'], True, f'domanda_{n}', test_to_render[n].domanda.tipo])
                Test.objects.filter(idTest=idTest).update(numeroErrori=F('numeroErrori') + 1)
                Statistiche.objects.filter(utente=req.user, tipoDomanda='m').update(nrErrori=F('nrErrori') + 1)
                if len(errors) == 0:
                    errors.append({'pagina': displayer, f'domanda_{n}_multipla': user_input})
            else:
                
                corrected_errors.append({'pagina': displayer, 'domanda': f'domanda_{n}', 'errore': user_input})
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', test_to_render[n].domanda.tipo])

        elif domande_to_render[n] == 'cr':
            user_input = req.POST.get(f'domanda_{n}')
            if user_input != '1':
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta[f'domanda_{n}'], True, f'domanda_{n}', test_to_render[n].domanda.tipo])
                Statistiche.objects.filter(utente=req.user, tipoDomanda=formRisposta[f'domanda_{n}'].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)
                Test.objects.filter(idTest=idTest).update(numeroErrori=F('numeroErrori') + 1)
                if len(errors) == 0:
                    errors.append({'pagina': displayer, f'domanda_{n}': user_input})
            else:
                corrected_errors.append({'pagina': displayer, 'domanda': f'domanda_{n}', 'errore': user_input})
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', test_to_render[n].domanda.tipo])

            form_data[f'domanda_{n}'] = user_input

        else:
            user_input = req.POST.get(f'domanda_{n}')
            if user_input != test_to_render[n].variante.rispostaEsatta:
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta[f'domanda_{n}'], True, f'domanda_{n}', test_to_render[n].domanda.tipo])
                Statistiche.objects.filter(utente=req.user, tipoDomanda=formRisposta[f'domanda_{n}'].field.widget.input_type[0]).update(nrErrori=F('nrErrori') + 1)
                Test.objects.filter(idTest=idTest).update(numeroErrori=F('numeroErrori') + 1)
                if len(errors) == 0:
                    errors.append({'pagina': displayer, f'domanda_{n}': user_input})
            else:
                corrected_errors.append({'pagina': displayer, 'domanda': f'domanda_{n}', 'errore': user_input})
                ctx.append([test_to_render[n].domanda, test_to_render[n].variante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', test_to_render[n].domanda.tipo])

            form_data[f'domanda_{n}'] = user_input

    # Rimuovi errori corretti dagli errori ancora esistenti
    for ce in corrected_errors:
        existing_errors = [error for error in existing_errors if not (error['pagina'] == ce['pagina'] and list(error.keys())[1] == ce['domanda'])]

    combined_errors = existing_errors + errors

    # Salva errori in sessione
    if not req.session.get('Errori'):
        req.session['Errori'] = combined_errors

    req.session[f'form_data_page_{displayer}'] = form_data
    req.session.save()

    return ctx, corrected_errors








### FUNZIONI DI GENERAZIONE ###

# Genera opzioni di risposta statiche per le CR, random per tutto il resto
def generaOpzioniRisposta(formRisposta, test_to_render, seed):
    for n, formDomanda in enumerate(test_to_render):
        if formDomanda.domanda.tipo == 'cr':
            choices = genRandomStaticAnswers('cr', formDomanda.variante.rispostaEsatta)
        else:
            choices, _ = genRandomFromSeed(formDomanda.domanda.tipo, seed, formDomanda.variante.rispostaEsatta)
        formRisposta.fields[f'domanda_{n}'].choices = choices


# Non c'è rischio num > 9 perchè questa funzione viene chiamata solo per numeri a singole cifre, da 0 a 9
def genRandomint(num):
    lower_bound = 0  # Minimo numero generabile
    upper_bound = 9  # Massimo numero generabile

    if num <= lower_bound:
        return num + 1
    elif num >= upper_bound:
        return num - 1
    else:
        if randint(0, 1) == 0:
            return randint(lower_bound, num - 1)
        else:
            return randint(num + 1, upper_bound)


def randomGen(lungh, to_repl):
    ret = random.choices(string.ascii_lowercase, k=lungh)
    while ret == to_repl:
        ret = random.choices(string.ascii_lowercase, k=lungh)

    return ret[0]


def genRandomFromSeed(tipo, seed, rispostaGiusta):
    if tipo == 's':
        app_list = list()
        app_list.append(('', '- selezionare opzione -'))

        if len(rispostaGiusta) == 1 and str(rispostaGiusta).isdigit():
            for _ in range(0, randint(5, 9)):
                num = int(rispostaGiusta)
                var = genRandomint(num)
                app_list.append((str(_), str(var)))
            app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
            ret = app_list
        else:
            for _ in range(0, randint(5, 9)):
                var = str(rispostaGiusta)
                to_repl = var[randint(0, len(var) - 1)]
                var = var.replace(to_repl, randomGen(1, to_repl))
                if str(var) != str(rispostaGiusta):
                    app_list.append((str(_), var))
            app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
            ret = app_list

    else:
        app_list = list()

        if len(rispostaGiusta) == 1 and str(rispostaGiusta).isdigit():
            for _ in range(0, randint(5, 9)):
                num = int(rispostaGiusta)
                var = genRandomint(num)
                app_list.append((str(_), str(var)))
            app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
            ret = app_list
        else:
            for _ in range(0, randint(5, 9)):
                var = str(rispostaGiusta)
                to_repl = var[randint(0, len(var) - 1)]
                var = var.replace(to_repl, randomGen(1, to_repl))
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
    return ret, seed


def genRandomStaticAnswers(tipo, rispostaGiusta):
    ret = []

    if tipo == 'cr':
        ret.append(('1', rispostaGiusta))

        if rispostaGiusta == '* Accetto i termini e condizioni sulla privacy e sul trattamento dei dati personali':
            ret.append(('2', '* Non accetto i termini e condizioni sulla privacy e sul trattamento dei dati personali'))
        elif rispostaGiusta == 'Accetto i termini del bando':
            ret.append(('2', 'Non accetto i termini del bando'))
        elif rispostaGiusta == 'Accetto i termini del contratto':
            ret.append(('2', 'Non accetto i termini del contratto'))

        random.shuffle(ret)

    return ret

###


def reformat_date(input_date):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%d-%m-%Y %H:%M')  # Esempio: 31-01-2024 15:23

    if isinstance(input_date, date):
        iso_date = timezone.datetime.strftime(input_date, '%Y-%m-%dT%H:%M:%S')
        print(iso_date)
        return iso_date
    else:
        raise ValueError("Tipo di input non supportato per formattazione data")


def validateDynamicQuestions(formDomanda):
    if 'domani' in formDomanda.corpo:
        correct_answer = datetime.now().strftime("%Y/%m/%d")
        if formDomanda.risposta == correct_answer:
            return True
        else:
            return False
    return 'continua...'



def print_sessione(req):
    print("Errori: ", req.session.get('Errori'))

    form_data_keys = [key for key in req.session.keys() if key.startswith('form_data_page')]
    for key in form_data_keys:
        print(f"{key}: {req.session[key]}")


def pulisci_sessione(req):
    if 'Errori' in req.session:
        del req.session['Errori']
    form_data_keys = [key for key in req.session.keys() if key.startswith('form_data_page')]
    for key in form_data_keys:
        del req.session[key]
