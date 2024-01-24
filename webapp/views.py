from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from webapp.models import Utenti, Domande, Varianti, Test, Test_Utenti
from django.http import Http404
from django.contrib.auth import authenticate, login, logout 
from django.core.exceptions import SuspiciousOperation
from .forms import LoginForm, TestManualeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
                messages.error(req, 'username o password non corretti')    
            
    return render(req, "login/login.html")


@login_required(login_url='login')
def home(req):
    return render(req, 'home/home.html')

@login_required(login_url='login')
def creazioneTest(req):
    form = TestManualeForm()
    context = {"creaTestManualeForm": form}
    return render(req, 'test/creazioneTest.html', context)




@login_required(login_url='login')
def creaTestManuale(req):
    if req.method == 'POST':
        form = TestManualeForm(req.POST)
        if form.is_valid():
            testNumber = form.cleaned_data['testNumber']
            inSequenza = form.cleaned_data['inSequenza']
            secondiRitardo = form.cleaned_data['secondiRitardo']
            print("testNumber",testNumber)
            print("inSequenza",inSequenza)
            print("secondiRitardo",secondiRitardo)
            # crea Form su DB

    return render(req, 'test/creazioneTest.html')
    



@login_required(login_url='login')
def preTest(req, test_id):
    try:
        test = Test.objects.get(idTest=test_id)
        print(test)
    except Test.DoesNotExist:
        raise Http404("Test non esistente")
    return render(req, "test/preTest.html", { "test": test, })