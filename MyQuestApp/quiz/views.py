from django.shortcuts import render, HttpResponse

def index(req):
    
    return render(req, "quiz/index.html")

def main(req):

    return render(req, 'quiz/main.html')

def test(req):

    return render(req, 'quiz/test.html')



# Create your views here.
