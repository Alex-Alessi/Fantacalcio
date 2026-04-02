from django.shortcuts import render
from .models import Giornata, PartitaLega
from django.utils import timezone
from django.db.models import Q

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
    ultima_giocata = PartitaLega.objects.filter(giornata__finita=True).filter(
        Q(squadra_casa__primo_allenatore=request.user.profile)|
        Q(squadra_casa__secondo_allenatore=request.user.profile)|
        Q(squadra_ospite__primo_allenatore=request.user.profile)|
        Q(squadra_ospite__secondo_allenatore=request.user.profile)
    ).order_by('-giornata__orario_inizio').first()
    prossime = PartitaLega.objects.filter(giornata__finita=False).filter(
        Q(squadra_casa__primo_allenatore=request.user.profile)|
        Q(squadra_casa__secondo_allenatore=request.user.profile)|
        Q(squadra_ospite__primo_allenatore=request.user.profile)|
        Q(squadra_ospite__secondo_allenatore=request.user.profile)
    ).order_by('giornata__orario_inizio')
    count = prossime.count()
    if count > 1:
        prossima_partita=prossime[1]
    elif count == 1:
        prossima_partita = prossime[0]
    else:
        prossima_partita = None
    context={
        "giornata":giornata,
        "giornata_iniziata": giornata_iniziata,
        "tempo_rimanente": tempo_rimanente,
        "ultima_giocata": ultima_giocata,
        "prossima_partita": prossima_partita,
    }
    return render(request, "game/home.html", context)

