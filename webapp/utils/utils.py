from django.utils import timezone
from datetime import datetime, date
from random import randint
import random
import string


### FUNZIONI DI GENERAZIONE ###

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
    if True :
        if tipo == 's':
            app_list = list()
            app_list.append(('', '- selezionare opzione -'))
            
            if len(rispostaGiusta) == 1 and str(rispostaGiusta).isdigit() :
                for _ in range(0, randint(6,14)):
                    num = int(rispostaGiusta)
                    var = genRandomint(num)
                    app_list.append((str(_), str(var)))
                app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
                ret = app_list
            else:
                for _ in range(0, randint(6,14)):
                    var = str(rispostaGiusta)
                    to_repl = var[randint(0,len(var)-1)]
                    var  = var.replace(to_repl, randomGen(1, to_repl))
                    if str(var) != str(rispostaGiusta):
                        app_list.append((str(_), var))
                app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
                ret = app_list
            
        else:
            app_list = list()

            if len(rispostaGiusta) == 1 and str(rispostaGiusta).isdigit() :
                for _ in range(0, randint(6,14)):
                    num = int(rispostaGiusta)
                    var = genRandomint(num)
                    app_list.append((str(_), str(var)))
                app_list.append((str(rispostaGiusta), str(rispostaGiusta)))
                ret = app_list
            else:
                for _ in range(0, randint(6,14)):
                    var = str(rispostaGiusta)
                    to_repl = var[randint(0,len(var)-1)]
                    var  = var.replace(to_repl, randomGen(1, to_repl))
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
        elif rispostaGiusta == 'Accetto i termini del contratto':
            ret.append(('2', 'Non accetto i termini del contratto'))  

        random.shuffle(ret) 
        
    return ret

###



def reformat_date(input_date):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%d-%m-%Y %H:%M') # Esempio: 31-01-2024 15:23

    if isinstance(input_date, date):
        iso_date = timezone.datetime.strftime(input_date, '%Y-%m-%dT%H:%M:%S')
        print(iso_date)
        return iso_date
    else:
        raise ValueError("Tipo di input non supportato per formattazione data")
