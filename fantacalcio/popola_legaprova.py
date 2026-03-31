from django.contrib.auth import get_user_model
from accounts.models import Profile
from game.models import *
from game.utils import calcola_giornata
from random import randint, choice

User = get_user_model()

# ---------------------------
# RESET (facoltativo)
# ---------------------------
Lega.objects.all().delete()
Squadra.objects.all().delete()
Classifica.objects.all().delete()
Giocatore.objects.all().delete()
Giornata.objects.all().delete()
PartitaLega.objects.all().delete()
Statistiche.objects.all().delete()
Formazione.objects.all().delete()
GiocatoreSchierato.objects.all().delete()
BonusMalus.objects.all().delete()
ImpostazioniPunteggio.objects.all().delete()
User.objects.filter(username__in=["admin_test","user2_test"]).delete()

# ---------------------------
# 1️⃣ UTENTI + LEGA
# ---------------------------
user1 = User.objects.create(username="admin_test")
user1.set_password("1234")
user1.save()
user2 = User.objects.create(username="user2_test")
user2.set_password("1234")
user2.save()

lega = Lega.objects.create(admin=user1, name="Test League", partecipanti=4, crediti=500, password="")
lega.set_password("pass")
lega.save()

# ---------------------------
# 2️⃣ IMPOSTAZIONI + BONUS/MALUS
# ---------------------------
ImpostazioniPunteggio.objects.create(
    lega=lega,
    soglia_primo_gol=66.0,
    punti_gol_successivi=6.0
)
for ruolo in ['portiere', 'difensore', 'centrocampista', 'attaccante']:
    BonusMalus.objects.create(lega=lega, ruolo=ruolo)

# ---------------------------
# 3️⃣ PROFILI + SQUADRE
# ---------------------------
p1 = Profile.objects.create(user=user1)
p2 = Profile.objects.create(user=user2)

s1 = Squadra.objects.create(name="Team A", primo_allenatore=p1, lega=lega)
s2 = Squadra.objects.create(name="Team B", primo_allenatore=p2, lega=lega)

Classifica.objects.create(squadra=s1, lega=lega)
Classifica.objects.create(squadra=s2, lega=lega)

# ---------------------------
# 4️⃣ CREAZIONE GIOCATORI
# ---------------------------
giocatori = []
nomi = [("Mario","Rossi"), ("Luigi","Verdi"), ("Paolo","Bianchi"), ("Marco","Neri"),
        ("Anna","Gialli"), ("Sara","Blu"), ("Luca","Viola"), ("Giulia","Arancio")]

ruoli = ["portiere", "difensore", "centrocampista", "attaccante"]
for i, (nome, cognome) in enumerate(nomi):
    g = Giocatore.objects.create(
        name=nome,
        surname=cognome,
        squadra_reale=f"S{i+1}",
        data_nascita=f"199{i}-01-01",
        ruolo=choice(ruoli),
        altezza=170 + i*2,
        piede_preferito=choice(["destro","sinistro"]),
        nazionalità="IT",
        descrizione="Test"
    )
    giocatori.append(g)

# ---------------------------
# 5️⃣ ROSA SQUADRE
# ---------------------------
s1.rosa.add(*giocatori[:4])
s2.rosa.add(*giocatori[4:])

# ---------------------------
# 6️⃣ SIMULAZIONE GIORNATE
# ---------------------------
NUM_GIORNATE = 3

for g_num in range(1, NUM_GIORNATE + 1):
    giornata = Giornata.objects.create(giornata=g_num, finita=True, calcolata=False)

    # Creiamo le formazioni
    f1 = Formazione.objects.create(squadra=s1, giornata=giornata, modulo_scelto="4-3-3")
    f2 = Formazione.objects.create(squadra=s2, giornata=giornata, modulo_scelto="4-3-3")

    # Schieriamo tutti i giocatori
    for gioc in s1.rosa.all():
        GiocatoreSchierato.objects.create(formazione=f1, giocatore=gioc, stato="titolare")
    for gioc in s2.rosa.all():
        GiocatoreSchierato.objects.create(formazione=f2, giocatore=gioc, stato="titolare")

    # Statistiche casuali ma realistiche (totale squadra < soglia primo gol)
    for gioc in s1.rosa.all():
        Statistiche.objects.create(
            giocatore=gioc,
            giornata=giornata,
            voto=randint(5,7),       # voti moderati
            gol_fatti=randint(0,1)   # pochi gol, per non superare facilmente la soglia
        )
    for gioc in s2.rosa.all():
        Statistiche.objects.create(
            giocatore=gioc,
            giornata=giornata,
            voto=randint(6,10),
            gol_fatti=randint(0,10)
        )

    # Partita
    partita = PartitaLega.objects.create(
        giornata=giornata,
        squadra_casa=s1,
        squadra_ospite=s2
    )

    # Calcolo punteggi e classifica
    calcola_giornata(lega, giornata)
    partita.refresh_from_db()
    print(f"\nGiornata {g_num}:")
    print(f"Punti casa: {partita.punti_casa}, Gol casa: {partita.gol_casa}")
    print(f"Punti ospite: {partita.punti_ospite}, Gol ospite: {partita.gol_ospite}")

# ---------------------------
# 7️⃣ CLASSIFICA FINALE
# ---------------------------
print("\nCLASSIFICA FINALE:")
for c in Classifica.objects.filter(lega=lega).order_by('-punti'):
    print(
        c.squadra.name,
        "| Punti:", c.punti,
        "| V:", c.vittorie,
        "| N:", c.pareggi,
        "| P:", c.sconfitte,
        "| GF:", c.gol_fatti,
        "| GS:", c.gol_subiti
    )