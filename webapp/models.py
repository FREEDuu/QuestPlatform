from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max

class Domande(models.Model):
    idDomanda = models.AutoField(primary_key=True)
    corpo = models.CharField(max_length=100)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.corpo
    
    # @classmethod: when this method is called, we pass the class as the first argument instead of the instance of that class
    @classmethod
    def get_random_domanda(cls):
        random_domanda = cls.objects.order_by('?').first()
        return random_domanda


class Varianti(models.Model):
    idVariante = models.AutoField(primary_key=True)
    domanda = models.ForeignKey(Domande, on_delete=models.CASCADE)
    corpo = models.CharField(max_length=100)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.corpo
    
    @classmethod
    def get_random_variante(cls, idDomanda):
        random_variante = cls.objects.filter(domanda=idDomanda).order_by('?').first()
        return random_variante

class Test(models.Model):
    idTest = models.AutoField(primary_key=True)
    nrGruppo = models.IntegerField(default=0)
    tipo = models.CharField(max_length=50, default="manuale")
    inSequenza = models.BooleanField(null=False, default=False)
    secondiRitardo = models.IntegerField(default=1)
    durataMax = models.IntegerField(default=60)
    dataOraInizio = models.DateTimeField(null=True)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.idTest,self.nrGruppo,self.tipo)
    
    @classmethod
    def get_next_gruppo(cls):
        max_gruppo = cls.objects.aggregate(Max('nrGruppo'))['nrGruppo__max']
        return max_gruppo + 1 if max_gruppo is not None else 1

# Associa ad ogni singolo test uno o molteplici utenti
class Test_Utenti(models.Model):
    idTest_Utenti = models.AutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)


# Associa ad ogni singolo test molteplici domande, ognuna con la sua variante selezionata.
class Test_Domande_Varianti(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    domanda = models.ForeignKey(Domande, on_delete=models.CASCADE)
    variante = models.ForeignKey(Varianti, on_delete=models.CASCADE)

# Segna il tempo speso dall'utente per completare ogni test (altro?)
class Statistiche(models.Model):
    idStatistica = models.AutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    tempo = models.FloatField(default=0)


