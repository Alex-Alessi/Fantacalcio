from django.contrib import admin
from .models import Lega, Giocatore, Squadra, Giornata, ImpostazioniRosa, ImpostazioniMatch, BonusMalus, Statistiche, ImpostazioniPunteggio, Formazione, GiocatoreSchierato, PartitaLega, Classifica

# Register your models here.

admin.site.register(Lega)
admin.site.register(Giocatore)
admin.site.register(Squadra)
admin.site.register(Giornata)
admin.site.register(ImpostazioniRosa)
admin.site.register(ImpostazioniMatch)
admin.site.register(BonusMalus)
admin.site.register(Statistiche)
admin.site.register(ImpostazioniPunteggio)
admin.site.register(Formazione)
admin.site.register(GiocatoreSchierato)
admin.site.register(PartitaLega)
admin.site.register(Classifica)