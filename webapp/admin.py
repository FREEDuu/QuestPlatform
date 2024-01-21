from django.contrib import admin

from .models import Domande, Test, Test_Utenti, Varianti, Utenti
admin.site.register(Domande)
admin.site.register(Test)
admin.site.register(Test_Utenti)
admin.site.register(Varianti)
admin.site.register(Utenti)
