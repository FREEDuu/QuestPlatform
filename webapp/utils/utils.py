from django.utils import timezone
from datetime import datetime, date
from random import randint
import random
import string



def reformat_date(input_date):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%d-%m-%Y %H:%M') # Esempio: 31-01-2024 15:23

    if isinstance(input_date, date):
        iso_date = timezone.datetime.strftime(input_date, '%Y-%m-%dT%H:%M:%S')
        print(iso_date)
        return iso_date
    else:
        raise ValueError("Tipo di input non supportato per formattazione data")


def genRandomFromSeed(tipo, seed, rispostaGiusta):
    if str(rispostaGiusta).isdigit() :
        if tipo == 's':
            ret = [('', '- selezionare opzione -'), ('1',str(randint(0,9))),('2',str(randint(0,8))),(str(rispostaGiusta), str(rispostaGiusta))]
        else:
            ret = [('1',str(randint(0,9))),('2',str(randint(0,8))),(str(rispostaGiusta), str(rispostaGiusta))]

    else:
        if tipo == 's':
            ret = [('', '- selezionare opzione -'), ('1',''.join(random.choices(string.ascii_lowercase, k=len(rispostaGiusta)))),('2',''.join(random.choices(string.ascii_lowercase, k=len(rispostaGiusta)))),(str(rispostaGiusta), str(rispostaGiusta))]
        else:
            ret = [('1',''.join(random.choices(string.ascii_lowercase, k=len(rispostaGiusta)))),('2',''.join(random.choices(string.ascii_lowercase, k=len(rispostaGiusta)))),(str(rispostaGiusta), str(rispostaGiusta))]

    # Per le select mescolare tutto tranne il primo valore di default
    if tipo == 's':
        shuffled_options = ret[1:]
        random.shuffle(shuffled_options)
        ret[1:] = shuffled_options
    else:
        random.shuffle(ret)
    
    return ret , seed


def genRandomStaticAnswers(tipo, rispostaGiusta):
    cr_elements = ['Non Accetto i termini del bando1', 'Non Accetto2', 'Non Accetto3', 'Non Accetto4'] 
    ret = []
    
    if tipo == 'cr':
        ret.append(('1', rispostaGiusta))  
        
        if rispostaGiusta == '* Accetto i termini e condizioni sulla privacy e sul trattamento dei dati personali':
            ret.append(('2', '* Non accetto i termini e condizioni sulla privacy e sul trattamento dei dati personali'))  
        elif rispostaGiusta == 'Accetto i termini del bando':
            ret.append(('2', 'Non accetto i termini del bando'))  

        random.shuffle(ret) 
        
    return ret

