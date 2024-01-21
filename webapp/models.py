from django.db import models

class Utenti(models.Model):
    idUtente = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=30)
    cognome = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    ruolo = models.CharField(max_length=30)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)

class Domande(models.Model):
    idDomanda = models.AutoField(primary_key=True)
    corpo = models.CharField(max_length=100)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.corpo


class Varianti(models.Model):
    idVariante = models.AutoField(primary_key=True)
    domanda = models.ForeignKey(Domande, on_delete=models.CASCADE)
    corpo = models.CharField(max_length=100)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.corpo

class Test(models.Model):
    idTest = models.AutoField(primary_key=True)
    durataMax = models.IntegerField()
    dataOraInizio = models.DateTimeField(auto_now_add=True)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.durataMax)


class Test_Utenti(models.Model):
    idTest_Utenti = models.AutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    utente = models.ForeignKey(Utenti, on_delete=models.CASCADE)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
      
    