from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max


class Domande(models.Model):
    idDomanda = models.AutoField(primary_key=True)
    corpo = models.CharField(max_length=400)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=100, default='t')
    numeroPagine = models.IntegerField(default=-1)
    attivo = models.BooleanField(default=True)

    def __str__(self):
        return self.corpo

    @classmethod
    def get_random_domanda(cls):
        random_domanda = cls.objects.order_by('?').first()
        return random_domanda

    def get_risposte_esatte(self):
        return "; ".join(str(v.rispostaEsatta) for v in self.varianti_set.all())

    class Meta:
        indexes = [
            models.Index(fields=['corpo']),
            models.Index(fields=['dataOraInserimento']),
            models.Index(fields=['tipo']),
            models.Index(fields=['attivo'])
        ]


class Varianti(models.Model):
    idVariante = models.AutoField(primary_key=True)
    domanda = models.ForeignKey(Domande, on_delete=models.CASCADE)
    corpo = models.CharField(max_length=400)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    rispostaEsatta = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.corpo

    @classmethod
    def get_random_variante(cls, idDomanda):
        random_variante = cls.objects.filter(domanda=idDomanda).order_by('?').first()
        return random_variante

    class Meta:
        indexes = [
            models.Index(fields=['domanda']),
            models.Index(fields=['corpo']),
            models.Index(fields=['dataOraInserimento']),
        ]


class Test(models.Model):
    idTest = models.AutoField(primary_key=True)
    utente = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    nrGruppo = models.IntegerField(default=0)
    inSequenza = models.BooleanField(null=False, default=False)
    tipo = models.CharField(max_length=50, default="manuale")
    secondiRitardo = models.IntegerField(default=1)
    dataOraInizio = models.DateTimeField(null=True)
    nrTest = models.IntegerField(default=0)
    dataOraFine = models.DateTimeField(null=True)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    malusF5 = models.BooleanField(null=False, default=False)
    numeroErrori = models.IntegerField(default=0)

    def __str__(self):
        return f'id: {self.idTest} | nrGruppo: {self.nrGruppo} | tipo: {self.tipo} | inSequenza: {self.inSequenza} | malus: {self.malusF5} numeroErrori: {self.numeroErrori}'

    @classmethod
    def get_next_gruppo(cls):
        max_gruppo = cls.objects.aggregate(Max('nrGruppo'))['nrGruppo__max']
        return max_gruppo + 1 if max_gruppo is not None else 1

    class Meta:
        indexes = [
            models.Index(fields=['utente']),
            models.Index(fields=['nrGruppo']),
            models.Index(fields=['dataOraInizio']),
            models.Index(fields=['dataOraFine']),
            models.Index(fields=['tipo']),
        ]


class TestsGroup(models.Model):
    idGruppi = models.AutoField(primary_key=True)
    utente = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    nrTest = models.IntegerField(default=0)
    nrGruppo = models.IntegerField(default=0)
    tipo = models.CharField(max_length=50, default="manuale")
    inSequenza = models.BooleanField(null=False, default=False)
    secondiRitardo = models.IntegerField(default=1)
    dataOraInizio = models.DateTimeField(null=True)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'id: {self.idGruppi} | nrGruppo: {self.nrGruppo} | tipo: {self.tipo} | inSequenza: {self.inSequenza}'

    @classmethod
    def get_next_gruppo(cls):
        max_gruppo = cls.objects.aggregate(Max('nrGruppo'))['nrGruppo__max']
        return max_gruppo + 1 if max_gruppo is not None else 1

    class Meta:
        indexes = [
            models.Index(fields=['utente']),
            models.Index(fields=['dataOraInserimento']),
            models.Index(fields=['dataOraInizio']),
            models.Index(fields=['tipo']),
        ]


class Test_Domande_Varianti(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    domanda = models.ForeignKey(Domande, on_delete=models.CASCADE)
    variante = models.ForeignKey(Varianti, on_delete=models.CASCADE)
    nrPagina = models.IntegerField(default=0)

    def __str__(self):
        return f'idTest: {self.test.idTest} domanda: {self.domanda.corpo} variante: {self.variante.corpo}'

    class Meta:
        indexes = [
            models.Index(fields=['test']),
            models.Index(fields=['domanda']),
            models.Index(fields=['variante']),
        ]


class Statistiche(models.Model):
    utente = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    tipoDomanda = models.CharField(max_length=50, default="t")
    nrErrori = models.IntegerField(default=0)

    def __str__(self):
        return f'id: {self.utente} | nrGruppo: {self.tipoDomanda} | tipo: {self.nrErrori}'

    class Meta:
        indexes = [
            models.Index(fields=['utente'])
        ]


class Sfide(models.Model):
    idSfida = models.AutoField(primary_key=True)
    utente = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='utente')
    utenteSfidato = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='utenteSfidato')
    nrGruppo = models.IntegerField(default=0)
    tipo = models.CharField(max_length=50, default="sfida")
    secondiRitardo = models.IntegerField(default=1)
    dataOraInizio = models.DateTimeField(null=True)
    dataOraInserimento = models.DateTimeField(auto_now_add=True)
    vincitore = models.CharField(max_length=50, default="pareggio")

    def __str__(self):
        return f'id: {self.idSfida} | nrGruppo: {self.utente} | tipo: {self.utenteSfidato}'

    class Meta:
        indexes = [
            models.Index(fields=['utente']),
            models.Index(fields=['utenteSfidato']),
            models.Index(fields=['nrGruppo']),
            models.Index(fields=['dataOraInizio'])
        ]
