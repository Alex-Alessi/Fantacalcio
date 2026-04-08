from django.shortcuts import render, redirect
from .models import Giornata, PartitaLega, Lega
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import LegaForm, JoinLegaForm

# Create your views here.

@login_required(login_url='/accounts/login/')
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

@login_required(login_url='/accounts/login/')
def crea_lega_view(request):
    if request.method == "POST":
        form = LegaForm(request.POST)
        if form.is_valid():
            lega=Lega(
                admin = request.user,
                name = form.cleaned_data['name'],
                partecipanti = form.cleaned_data['partecipanti'],
                crediti = form.cleaned_data['crediti']
            )
            password = form.cleaned_data['password']
            if password:
                lega.set_password(password)
            lega.save()
            lega.membri.add(request.user)
            return redirect('home')
        else:
            return render(request, "game/crea_lega.html", {"form":form})
    else:
        form=LegaForm()
    return render(request, "game/crea_lega.html", {"form":form})

@login_required(login_url='/accounts/login/')
def join_lega_view(request):
    if request.method == "POST":
        form=JoinLegaForm(request.POST)
        if form.is_valid():
            Lega.objects.filter(name=form.cleaned_data['name'])
    else:
        form=JoinLegaForm()