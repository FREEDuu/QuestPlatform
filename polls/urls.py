from django.urls import path

from . import views

urlpatterns = [
    path("ciao", views.index, name="index"),
]