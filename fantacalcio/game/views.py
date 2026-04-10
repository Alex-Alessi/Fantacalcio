from django.shortcuts import render, redirect, get_object_or_404
from .models import Giornata, PartitaLega, Lega, Squadra
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import LegaForm, JoinLegaForm, PasswordLegaForm

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
    leghe=[]
    if request.method == "POST":
        form=JoinLegaForm(request.POST)
        if form.is_valid():
            leghe=Lega.objects.filter(name__istartswith=form.cleaned_data['name'])
            if not leghe.exists():
                form.add_error(None, "Nessuna lega trovata!")
    else:
        form=JoinLegaForm()
    return render(request, "game/cerca_lega.html", {"leghe":leghe, "form":form})

@login_required(login_url='/accounts/login/')
def dettaglio_lega(request, pk):
    lega=get_object_or_404(Lega, id=pk)
    if request.user in lega.membri.all():
        return redirect('dashboard_squadra', lega_id=lega.id)
    if lega.membri.count()>=lega.partecipanti:
        return redirect('home')
    if lega.password:
        if request.method == "POST":
            form=PasswordLegaForm(request.POST)
            if form.is_valid() and lega.check_password(form.cleaned_data['password']):
                lega.membri.add(request.user)
                return redirect("dashboard_squadra", lega_id=lega.id)
            else:
                form.add_error(None, "Password errata")
        else:
            form=PasswordLegaForm()
        return render(request, "game/passkey_lega.html", {"form":form})
    else:
        lega.membri.add(request.user)
        return redirect('dashboard_squadra', lega_id=lega.id)
    
@login_required(login_url='/accounts/login/')
def dashboard_squadra(request, pk):
    lega=get_object_or_404(Lega, id=pk)
    if lega.membri.filter(id=request.user.id).exists():
        is_admin=False
        if request.user == lega.admin:
            is_admin=True
            is_free=True
            if lega.squadre.filter(Squadra.allenatore_principale.id=request.user.id or ):

        context={'lega':lega, 'is_admin':is_admin}
        return render(request, "game/dashboard_squadra.html", context)
    else:
        return redirect('home')