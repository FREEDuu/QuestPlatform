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


def genRandomFromSeed(seed, rispostaGiusta):
    random.seed(seed)
    ret = [('1',str(randint(0,9))),('2',str(randint(0,8))),(str(rispostaGiusta), str(rispostaGiusta))]
    random.shuffle(ret)
    return ret , seed+1


def genRandomStaticAnswers(tipo, rispostaGiusta):
    cr_elements = ['Non Accetto i termini del bando1', 'Non Accetto2', 'Non Accetto3', 'Non Accetto4'] 
    ret = []
    
    if tipo == 'cr':
        ret.append(('1', rispostaGiusta))  
        
        if rispostaGiusta == '* Accetto i termini e le condizioni sulla privacy':
            ret.append(('2', '* Non accetto i termini e le condizioni sulla privacy'))  
        elif rispostaGiusta == 'Accetto i termini del bando':
            ret.append(('2', 'Non accetto i termini del bando'))  

        random.shuffle(ret) 
        
    return ret

