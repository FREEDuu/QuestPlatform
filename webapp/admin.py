from django.contrib import admin

from .models import Domande, Test, Test_Domande_Varianti, Varianti, Statistiche

class TestAdmin(admin.ModelAdmin):
    list_display = ["idTest", "nrGruppo", "tipo", "inSequenza", "dataOraInizio"]

class VariantiAdmin(admin.ModelAdmin):
    list_display = ["idVariante", "domanda", "corpo"]

class StatisticheAdmin(admin.ModelAdmin):
    list_display = ["idStatistica", "utente", "test", "tempo"]


class Test_Domande_VariantiAdmin(admin.ModelAdmin):
    list_display = ["test", "domanda", "variante"]

admin.site.register(Domande)
admin.site.register(Test, TestAdmin)
admin.site.register(Test_Domande_Varianti, Test_Domande_VariantiAdmin)
admin.site.register(Varianti, VariantiAdmin)
admin.site.register(Statistiche, StatisticheAdmin)
