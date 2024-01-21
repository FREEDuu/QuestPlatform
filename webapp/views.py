from django.shortcuts import render, HttpResponse
from django.template import loader
from webapp.models import Utenti, Domande, Varianti, Test, Test_Utenti
from django.http import Http404

def login(req):
    return render(req, "login/login.html")

def home(req):
    return render(req, 'home/home.html')

def test(req):
    return render(req, 'test/test.html')


def preTest(req, test_id):
    try:
        test = Test.objects.get(idTest=test_id)
        print(test)
    except Test.DoesNotExist:
        raise Http404("Test non esistente")
    return render(req, "test/preTest.html", { "test": test, })