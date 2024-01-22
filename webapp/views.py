from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from webapp.models import Utenti, Domande, Varianti, Test, Test_Utenti
from django.http import Http404
from django.contrib.auth import authenticate, login, logout 
from django.core.exceptions import SuspiciousOperation
from .forms import LoginForm
from django.contrib import messages

def log_in(req):

    logout(req)

    if req.method == 'POST':
        print('ENTER POST')
        form = LoginForm(req.POST)
        
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(req, username=username, password=password)

            if user is not None:
                login(req, user)
                
                return redirect('home')
            else :
                
                return HttpResponse('passowrd o username sbagliato/i')    
            
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