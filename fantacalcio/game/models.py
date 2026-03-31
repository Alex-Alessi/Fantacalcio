from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from accounts.models import Profile
from django.core.validators import MinValueValidator, MaxValueValidator
from multiselectfield import MultiSelectField
from django.db.models import Avg, Q
from django.conf import settings

# Create your models here.

PARTECIPANTI_CHOICES = [
    (4, '4'),
    (6, '6'),
    (8, '8'),
    (10, '10'),
    (12, '12'),
    (14, '14'),
    (16, '16'),
]

CREDITI_CHOICES = [
    (100, '100'),
    (250, '250'),
    (500, '500'),
    (1000, '1000'),
]

RUOLO_CHOICES = [
    ('portiere', 'P'),
    ('difensore', 'D'),
    ('centrocampista', 'C'),
    ('attaccante', 'A'),
]

PIEDE_CHOICES = [
    ('destro', 'Dx'),
    ('sinistro', 'Sx'),
]

VOTO_CHOICES = [
    (0, '0'),
    (0.5, '0.5'),
    (1, '1'),
    (1.5, '1.5'),
    (2, '2'),
    (2.5, '2.5'),
    (3, '3'),
    (3.5, '3.5'),
    (4, '4'),
    (4.5, '4.5'),
    (5, '5'),
    (5.5, '5.5'),
    (6, '6'),
    (6.5, '6.5'),
    (7, '7'),
    (7.5, '7.5'),
    (8, '8'),
    (8.5, '8.5'),
    (9, '9'),
    (9.5, '9.5'),
    (10, '10'),
]

PORTIERI_MIN = 1
PORTIERI_MAX = 15

DIFENSORI_MIN = 6
DIFENSORI_MAX = 25

CENTROCAMPISTI_MIN = 6
CENTROCAMPISTI_MAX = 25

ATTACCANTI_MIN = 4
ATTACCANTI_MAX = 25

SOSTITUZIONI_MIN = 0
SOSTITUZIONI_MAX = 10

FORMAZIONE_CHOICES=[
    ('3-4-3', '3-4-3'),
    ('3-5-2', '3-5-2'),
    ('4-3-3', '4-3-3'),
    ('4-4-2', '4-4-2'),
    ('4-5-1', '4-5-1'),
    ('5-3-2', '5-3-2'),
    ('5-4-1', '5-4-1'),
]

PANCHINA_CHOICES=[
    ('libera', 'Libera'),
    ('vincolata_ruolo', 'Vincolata al ruolo')
]

SWITCH_CHOICES=[
    ('nessuno', 'Nessuno'),
    ('base', 'Base'),
    ('plus', 'Plus')
]

STATO_CHOICES=[
    ('titolare', 'Titolare'),
    ('panchina', 'Panchina'),
]

class Lega(models.Model):
    admin=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name=models.CharField(max_length=30)
    partecipanti=models.IntegerField(choices=PARTECIPANTI_CHOICES)
    password = models.CharField(max_length=128)
    crediti = models.IntegerField(choices=CREDITI_CHOICES)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class Giocatore(models.Model):
    name=models.CharField(max_length=100)
    surname=models.CharField(max_length=100)
    squadra_reale=models.CharField(max_length=100)
    data_nascita=models.DateField()
    ruolo=models.CharField(choices=RUOLO_CHOICES)
    altezza=models.IntegerField(validators=[
            MinValueValidator(140),
            MaxValueValidator(230)
        ])
    piede_preferito=models.CharField(choices=PIEDE_CHOICES)
    nazionalità=models.CharField(max_length=100)
    photo=models.ImageField(upload_to='foto/', blank=True, default='foto/user.png')
    descrizione=models.CharField(max_length=500)

    def calcola_media(self):
        media=self.statistiche_set.aggregate(media=Avg('voto'))['media']
        return media if media is not None else 0
    
    def calcola_fantamedia(self):
        fantamedia=self.statistiche_set.aggregate(fantamedia=Avg('fantavoto'))['fantamedia']
        return fantamedia if fantamedia is not None else 0

class Squadra(models.Model):
    name=models.CharField(max_length=30)
    logo=models.ImageField(upload_to='logo/', blank=True, default='logo/logo.webp')
    primo_allenatore = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='allenatore_principale')
    secondo_allenatore = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="vice_allenatore", null=True, blank=True)
    lega = models.ForeignKey(Lega, on_delete=models.CASCADE)
    rosa = models.ManyToManyField(Giocatore)

    def __str__(self):
        return self.name

class Giornata(models.Model):
    giornata=models.PositiveIntegerField()
    finita=models.BooleanField(default=False)
    calcolata=models.BooleanField(default=False)

class ImpostazioniRosa(models.Model):
    lega=models.OneToOneField(Lega, on_delete=models.CASCADE)
    numero_portieri=models.IntegerField(validators=[MinValueValidator(PORTIERI_MIN), MaxValueValidator(PORTIERI_MAX)])
    numero_difensori=models.IntegerField(validators=[MinValueValidator(DIFENSORI_MIN), MaxValueValidator(DIFENSORI_MAX)])
    numero_centrocampisti=models.IntegerField(validators=[MinValueValidator(CENTROCAMPISTI_MIN), MaxValueValidator(CENTROCAMPISTI_MAX)])
    numero_attaccanti=models.IntegerField(validators=[MinValueValidator(ATTACCANTI_MIN), MaxValueValidator(ATTACCANTI_MAX)])

class ImpostazioniMatch(models.Model):
    lega=models.OneToOneField(Lega, on_delete=models.CASCADE)
    moduli=MultiSelectField(choices=FORMAZIONE_CHOICES)
    posti_panchina=models.IntegerField(validators=[MinValueValidator(7), MaxValueValidator(15)])
    tipo_panchina=models.CharField(choices=PANCHINA_CHOICES)
    num_sostituzioni=models.IntegerField(validators=[MinValueValidator(SOSTITUZIONI_MIN), MaxValueValidator(SOSTITUZIONI_MAX)])
    tipo_switch=models.CharField(choices=SWITCH_CHOICES, default='nessuno')

class BonusMalus(models.Model):
    lega=models.ForeignKey(Lega, on_delete=models.CASCADE)
    ruolo=models.CharField(choices=RUOLO_CHOICES)
    valore_gol=models.FloatField(default=3.0)
    gol_subito=models.FloatField(default=1.0)
    valore_assist=models.FloatField(default=1.0)
    valore_ammonizione=models.FloatField(default=0.5)
    rigori_segnati=models.FloatField(default=3.0)
    rigori_sbagliati=models.FloatField(default=3.0)
    rigori_parati=models.FloatField(default=3.0)
    valore_espulsione=models.FloatField(default=1.0)
    contributi_al_gol=models.FloatField(default=0)
    assist_soft=models.FloatField(default=1.0)
    assist_gold=models.FloatField(default=1.0)
    autogol=models.FloatField(default=2.0)
    gol_pareggio=models.FloatField(default=0)
    gol_vittoria=models.FloatField(default=0)
    porta_inviolata=models.FloatField(default=1)
    player_of_the_match=models.FloatField(default=0)

class Statistiche(models.Model):
    giocatore=models.ForeignKey(Giocatore, on_delete=models.CASCADE)
    giornata=models.ForeignKey(Giornata, on_delete=models.CASCADE)
    voto=models.FloatField(choices=VOTO_CHOICES)
    fantavoto=models.FloatField(default=0.0)
    gol_fatti=models.PositiveIntegerField(default=0)
    assist=models.PositiveIntegerField(default=0)
    ammonizioni=models.PositiveIntegerField(default=0)
    espulsioni=models.PositiveIntegerField(default=0)
    gol_subiti=models.PositiveIntegerField(default=0)
    rigori_parati=models.PositiveIntegerField(default=0)
    assist_soft = models.PositiveIntegerField(default=0)
    assist_gold = models.PositiveIntegerField(default=0)
    contributi_al_gol = models.PositiveIntegerField(default=0)
    gol_pareggio = models.PositiveIntegerField(default=0)
    gol_vittoria = models.PositiveIntegerField(default=0)
    player_of_the_match = models.BooleanField(default=False)

    def calcola_fantavoto_live(self, lega):
        regole=BonusMalus.objects.get(lega=lega, ruolo=self.giocatore.ruolo)
        fantavoto=self.voto
        fantavoto += (self.gol_fatti * regole.valore_gol)
        fantavoto += (self.assist * regole.valore_assist)
        fantavoto += (self.rigori_parati * regole.rigori_parati)
        fantavoto += (self.gol_vittoria * regole.gol_vittoria)
        fantavoto += (self.gol_pareggio * regole.gol_pareggio)
        fantavoto -= (self.ammonizioni * regole.valore_ammonizione)
        fantavoto -= (self.espulsioni * regole.valore_espulsione)
        fantavoto -= (self.gol_subiti * regole.gol_subito)
        if self.player_of_the_match:
            fantavoto += regole.player_of_the_match
        return fantavoto
    
    def aggiorna_fantavoto(self, lega):
        self.fantavoto=self.calcola_fantavoto_live(lega)
        self.save()

class ImpostazioniPunteggio(models.Model):
    lega=models.OneToOneField(Lega, on_delete=models.CASCADE)
    soglia_primo_gol=models.FloatField(default=66.0)
    punti_gol_successivi=models.FloatField(default=6.0)
    modificatore_difesa=models.BooleanField(default=False)

class Formazione(models.Model):
    squadra=models.ForeignKey(Squadra, on_delete=models.CASCADE)
    giornata=models.ForeignKey(Giornata, on_delete=models.CASCADE)
    modulo_scelto=models.CharField(default='4-3-3')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['squadra', 'giornata'],
                name='unique_formazione_per_squadra_per_giornata'
            )
        ]

class GiocatoreSchierato(models.Model):
    formazione=models.ForeignKey(Formazione, on_delete=models.CASCADE)
    giocatore=models.ForeignKey(Giocatore, on_delete=models.CASCADE)
    stato=models.CharField(choices=STATO_CHOICES, default='titolare')
    ordine_panchina=models.PositiveIntegerField(default=0)
    giocatore_sostituito_switch=models.ForeignKey(Giocatore, on_delete=models.SET_NULL, null=True, blank=True, related_name='switch_ricevuti')

class PartitaLega(models.Model):
    giornata=models.ForeignKey(Giornata, on_delete=models.CASCADE)
    squadra_casa=models.ForeignKey(Squadra, on_delete=models.CASCADE, related_name="squadra_casa")
    squadra_ospite=models.ForeignKey(Squadra, on_delete=models.CASCADE, related_name="squadra_ospite")
    punti_casa=models.FloatField(default=0.0)
    punti_ospite=models.FloatField(default=0.0)
    gol_casa=models.IntegerField(default=0)
    gol_ospite=models.IntegerField(default=0)
    status=models.BooleanField(default=False)

    def calcola_punti(self, lega, squadra):
        formazione=Formazione.objects.get(squadra=squadra, giornata=self.giornata)
        giocatori_schierati=GiocatoreSchierato.objects.filter(formazione=formazione)
        titolari=giocatori_schierati.filter(stato="titolare")
        tot=0
        for titolare in titolari:
            try:
                statistiche=Statistiche.objects.get(giocatore=titolare.giocatore, giornata=self.giornata)
                fantavoto=statistiche.calcola_fantavoto_live(lega=lega)
            except Statistiche.DoesNotExist:
                fantavoto=0
            tot+=fantavoto
        return tot

    def calcola_gol(self, lega):
        self.punti_casa = self.calcola_punti(lega=lega, squadra=self.squadra_casa)
        self.punti_ospite = self.calcola_punti(lega=lega, squadra=self.squadra_ospite)
        self.gol_casa = 0
        self.gol_ospite = 0
        self.save()

        if self.giornata.finita and not self.giornata.calcolata:
            impostazionipunteggio=ImpostazioniPunteggio.objects.get(lega=lega)
            soglia_primo_gol=impostazionipunteggio.soglia_primo_gol
            punti_gol_successivi=impostazionipunteggio.punti_gol_successivi
            while soglia_primo_gol<=self.punti_casa:
                self.gol_casa+=1
                soglia_primo_gol+=punti_gol_successivi
            soglia_primo_gol=impostazionipunteggio.soglia_primo_gol
            while soglia_primo_gol<=self.punti_ospite:
                self.gol_ospite+=1
                soglia_primo_gol+=punti_gol_successivi
            self.save()

class Classifica(models.Model):
    squadra=models.ForeignKey(Squadra, on_delete=models.CASCADE)
    lega=models.ForeignKey(Lega, on_delete=models.CASCADE)
    vittorie=models.IntegerField(default=0)
    pareggi=models.IntegerField(default=0)
    sconfitte=models.IntegerField(default=0)
    gol_fatti=models.IntegerField(default=0)
    gol_subiti=models.IntegerField(default=0)
    differenza_reti=models.IntegerField(default=0)
    punti=models.IntegerField(default=0)
    punti_totali=models.FloatField(default=0.0)

    def risultati(self, lega, giornata):
        partita=PartitaLega.objects.filter(Q(squadra_casa=self.squadra) | Q(squadra_ospite=self.squadra), giornata=giornata).first()
        
        if not partita:
            return
        
        if partita.squadra_casa==self.squadra:
            gol_fatti=partita.gol_casa
            gol_subiti=partita.gol_ospite
            if gol_fatti>gol_subiti:
                self.vittorie+=1
                self.punti+=3
            elif gol_fatti==gol_subiti:
                self.pareggi+=1
                self.punti+=1
            else:
                self.sconfitte+=1
                self.punti+=0
            self.gol_fatti+=gol_fatti
            self.gol_subiti+=gol_subiti
            self.differenza_reti=self.gol_fatti-self.gol_subiti
            self.punti_totali+=partita.punti_casa
            self.save()
        else:
            gol_fatti=partita.gol_ospite
            gol_subiti=partita.gol_casa
            if gol_fatti>gol_subiti:
                self.vittorie+=1
                self.punti+=3
            elif gol_fatti==gol_subiti:
                self.pareggi+=1
                self.punti+=1
            else:
                self.sconfitte+=1
                self.punti+=0
            self.gol_fatti+=gol_fatti
            self.gol_subiti+=gol_subiti
            self.differenza_reti=self.gol_fatti-self.gol_subiti
            self.punti_totali+=partita.punti_ospite
            self.save()
