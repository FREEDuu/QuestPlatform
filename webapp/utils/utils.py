# utils.py
from django.utils import timezone
from datetime import datetime, date
from random import randint
import random
import string
from django.db.models import F
from ..utils import queries
import time 

### VALIDAZIONE ###
def Validazione(req, formRisposta, domande_to_render, idTest, test_to_render, risposte_esatte, displayer):
    ctx = []
    errors = []
    corrected_errors = []
    form_data = {}

    existing_errors = req.session.get('Errori', [])
    stats_updates = []
    test_updates = []
    new_stats = []

    for n in range(len(domande_to_render)):
        if domande_to_render[n] == 'm':
            concat_string = ''
            for i in range(len(risposte_esatte[n])):
                user_input = req.POST.get(f'domanda_{n}_{i}')
                concat_string = ''.join([concat_string, user_input])

                # Salva tutti gli input
                form_data[f'domanda_{n}_{i}'] = user_input

            if concat_string != test_to_render[n].rispostaEsatta:
                ctx.append([test_to_render[n].corpoDomanda, test_to_render[n].corpoVariante, formRisposta[f'domanda_{n}'], True, f'domanda_{n}', test_to_render[n].tipo])
                if queries.check_statistica_esistente('m', req.user.id):
                    stats_updates.append((req.user.id, 'm'))
                else:
                    new_stats.append((req.user.id, 'm'))
                test_updates.append(idTest)
                
                if len(errors) == 0:
                    errors.append({'pagina': displayer, f'domanda_{n}_multipla': user_input})
            else:
                corrected_errors.append({'pagina': displayer, 'domanda': f'domanda_{n}_multipla', 'errore': user_input})
                ctx.append([test_to_render[n].corpoDomanda, test_to_render[n].corpoVariante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', test_to_render[n].tipo])

        elif domande_to_render[n] == 'cr':
            user_input = req.POST.get(f'domanda_{n}')
            if user_input != '1':
                ctx.append([test_to_render[n].corpoDomanda, test_to_render[n].corpoVariante, formRisposta[f'domanda_{n}'], True, f'domanda_{n}', test_to_render[n].tipo])
                if queries.check_statistica_esistente('cr', req.user.id):
                    stats_updates.append((req.user.id, 'cr'))
                else:
                    new_stats.append((req.user.id, 'cr'))
                test_updates.append(idTest)

                if len(errors) == 0:
                    errors.append({'pagina': displayer, f'domanda_{n}': user_input})
            else:
                corrected_errors.append({'pagina': displayer, 'domanda': f'domanda_{n}', 'errore': user_input})
                ctx.append([test_to_render[n].corpoDomanda, test_to_render[n].corpoVariante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', test_to_render[n].tipo])

            form_data[f'domanda_{n}'] = user_input

        else:
            user_input = req.POST.get(f'domanda_{n}')
            if user_input != test_to_render[n].rispostaEsatta:
                ctx.append([test_to_render[n].corpoDomanda, test_to_render[n].corpoVariante, formRisposta[f'domanda_{n}'], True, f'domanda_{n}', test_to_render[n].tipo])
                if queries.check_statistica_esistente(test_to_render[n].tipo, req.user.id):
                    stats_updates.append((req.user.id, test_to_render[n].tipo))
                else:
                    new_stats.append((req.user.id, test_to_render[n].tipo))
                test_updates.append(idTest)

                if len(errors) == 0:
                    errors.append({'pagina': displayer, f'domanda_{n}': user_input})
            else:
                corrected_errors.append({'pagina': displayer, 'domanda': f'domanda_{n}', 'errore': user_input})
                ctx.append([test_to_render[n].corpoDomanda, test_to_render[n].corpoVariante, formRisposta[f'domanda_{n}'], False, f'domanda_{n}', test_to_render[n].tipo])

            form_data[f'domanda_{n}'] = user_input

    # Bulk update/insert statistiche
    queries.bulk_update_statistiche(stats_updates)
    queries.bulk_insert_nuova_statistica(new_stats)
    queries.bulk_update_test_numero_errori(test_updates)

    # Rimuovi errori corretti dagli errori ancora esistenti
    for ce in corrected_errors:
        existing_errors = [error for error in existing_errors if not (error['pagina'] == ce['pagina'] and list(error.keys())[1] == ce['domanda'])]

    combined_errors = existing_errors + errors

    # Salva errori in sessione
    req.session['Errori'] = combined_errors

    req.session[f'form_data_page_{displayer}'] = form_data
    req.session.save()

    return ctx, corrected_errors
# 



### GENERIC TEST ###

def repopulate_form(formRisposta, form_data, test_to_render, risposte_esatte, displayer, errors):
    if errors:
        check1 = errors[0]['pagina']
        check2 = list(errors[0].keys())[1]
    else:
        check1 = '4'
        check2 = 'ciao_'

    multiple = {}
    for key, value in form_data.items():
        if key != 'csrfmiddlewaretoken':
            parts = key.split('_')
            if len(parts) >= 2 and parts[1].isdigit():
                chiave = parts[0] + '_' + parts[1]
                index = int(parts[1])

                if len(parts) == 3:
                    controllo = risposte_esatte[index]

                    if chiave in multiple.keys():
                        if value == '':
                            multiple[chiave] += ' '
                        else:
                            multiple[chiave] += value
                    else:
                        if value == ' ':
                            multiple[chiave] = ' '
                        else:
                            multiple[chiave] = value
                    formRisposta.fields[chiave].initial = multiple[chiave]

                    if multiple.get(chiave) is not None and len(multiple[chiave]) == len(risposte_esatte[index]):
                        for i in range(len(controllo)):
                            concat_string = multiple[chiave]
                            if concat_string[i] != controllo[i]:
                                formRisposta.fields['domanda_{}'.format(index)].widget.widgets[i].attrs.update({'style': 'width: 38px; margin-right: 10px; border: 1px solid red;'})
                else:
                    formRisposta.fields[key].initial = value

    return [(row.corpoDomanda, row.corpoVariante, formRisposta[f'domanda_{n}'], check2 == f'domanda_{n}' and int(check1) == displayer, f'domanda_{n}', row.tipo) for n, row in enumerate(test_to_render)]

###





### FUNZIONI DI GENERAZIONE ###

# Genera opzioni di risposta statiche per le CR, random per tutto il resto
def generaOpzioniRisposta(formRisposta, test_to_render, seed):
    for n, formDomanda in enumerate(test_to_render):
        if formDomanda.tipo == 'cr':
            choices = genRandomStaticAnswers('cr', formDomanda.rispostaEsatta)
        else:
            choices, _ = genRandomFromSeed(formDomanda.tipo, seed, formDomanda.rispostaEsatta)
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

