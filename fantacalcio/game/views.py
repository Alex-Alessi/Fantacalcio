from django.shortcuts import render
from .models import Giornata
from django.utils import timezone

# Create your views here.

def home(request):
    giornata=Giornata.objects.filter(finita=False).order_by('orario_inizio').first()
    giornata_iniziata=False
    tempo_rimanente=None
    now=timezone.now()
    if giornata and giornata.orario_inizio:
        giornata_iniziata = now >= giornata.orario_inizio
        if not giornata_iniziata:
            tempo_rimanente = (giornata.orario_inizio - now).total_seconds()
    context={
        "giornata":giornata,
        "giornata_iniziata": giornata_iniziata,
        "tempo_rimanente": tempo_rimanente,
    }
    return render(request, "game/home.html", context)