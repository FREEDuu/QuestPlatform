from django.contrib import admin

from .models import Domande, Test, Test_Domande_Varianti, Varianti, TestsGroup, Statistiche, Sfide

class TestAdmin(admin.ModelAdmin):
    list_display = ["idTest", "nrGruppo", "tipo", "inSequenza", "dataOraInizio"]

class VariantiAdmin(admin.ModelAdmin):
    list_display = ["idVariante", "domanda", "corpo"]

class Test_Domande_VariantiAdmin(admin.ModelAdmin):
    list_display = ["test", "domanda", "variante"]

admin.site.register(Domande)
admin.site.register(Test, TestAdmin)
admin.site.register(TestsGroup)
admin.site.register(Test_Domande_Varianti, Test_Domande_VariantiAdmin)
admin.site.register(Varianti, VariantiAdmin)
admin.site.register(Statistiche)
admin.site.register(Sfide)


