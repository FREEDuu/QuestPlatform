from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from ..models import *
from . import page_views

@login_required(login_url='login')
def delete_all_user_test(req):
    TestsGroup.objects.filter(utente = req.user.id).delete()

    return page_views.home(req) 

def cancella_un_test(req, idGruppi):
    TestsGroup.objects.filter(idGruppi = idGruppi).delete()

    return page_views.home(req)


def TestProgrammati(req, idTest):
    return HttpResponse(idTest)

