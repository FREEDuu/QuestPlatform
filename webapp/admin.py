from django.contrib import admin

from .models import Domande, Test, Test_Utenti, Test_Domande_Varianti, Varianti
admin.site.register(Domande)
admin.site.register(Test)
admin.site.register(Test_Utenti)
admin.site.register(Test_Domande_Varianti)
admin.site.register(Varianti)
