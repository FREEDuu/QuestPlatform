from django.shortcuts import render, HttpResponse

def login(req):
    
    return render(req, "login/login.html")

def home(req):

    return render(req, 'home/home.html')

def test(req):

    return render(req, 'home/test.html')



# Create your views here.
