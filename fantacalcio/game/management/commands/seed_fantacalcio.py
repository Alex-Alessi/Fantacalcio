from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from game.models import Lega, Squadra, Giornata, PartitaLega


class Command(BaseCommand):
    help = "Reset completo e generazione dati Fantacalcio"

    def handle(self, *args, **kwargs):

        self.stdout.write("Reset database...")

        PartitaLega.objects.all().delete()
        Giornata.objects.all().delete()
        Squadra.objects.all().delete()
        Lega.objects.all().delete()
        User.objects.filter(username__startswith="user").delete()

        # --- UTENTI ---
        self.stdout.write("Creazione utenti...")

        users = []

        for i in range(8):
            user = User.objects.create_user(
                username=f"user{i}",
                password="test123"
            )
            Profile.objects.get_or_create(user=user)
            users.append(user)

        # --- LEGA ---
        self.stdout.write("Creazione lega...")

        lega = Lega.objects.create(
            name="Lega Test",
            admin=users[0],
            partecipanti=8,
            crediti=500
        )

        lega.membri.set(users)

        # --- SQUADRE ---
        self.stdout.write("Creazione squadre...")

        squadre = []

        for i, user in enumerate(users):
            squadra = Squadra.objects.create(
                name=f"Squadra {i+1}",
                lega=lega,
                primo_allenatore=user.profile
            )
            squadre.append(squadra)

        # --- FUNZIONI CALENDARIO ---
        def genera_andata(squadre):
            squadre = squadre[:]
            andata = []

            for n in range(len(squadre) - 1):
                partite = []

                for i in range(len(squadre) // 2):
                    casa = squadre[i]
                    ospite = squadre[-(i + 1)]

                    if n % 2 == 1:
                        casa, ospite = ospite, casa

                    partite.append((casa, ospite))

                andata.append(partite)

                fisso = squadre[0]
                resto = squadre[1:]
                resto = resto[-1:] + resto[:-1]
                squadre = [fisso] + resto

            return andata

        def genera_ritorno(andata):
            ritorno = []

            for giornata in andata:
                invertita = []
                for casa, ospite in giornata:
                    invertita.append((ospite, casa))
                ritorno.append(invertita)

            return ritorno

        def ruota(squadre, shift=1):
            return squadre[shift:] + squadre[:shift]

        # --- GENERAZIONE CALENDARIO ---
        self.stdout.write("Generazione calendario...")

        squadre1 = squadre[:]
        squadre2 = ruota(squadre1, 1)
        squadre3 = ruota(squadre1, 2)

        andata1 = genera_andata(squadre1)
        andata2 = genera_andata(squadre2)
        andata3 = genera_andata(squadre3)

        ritorno1 = genera_ritorno(andata1)
        ritorno2 = genera_ritorno(andata2)
        ritorno3 = genera_ritorno(andata3)

        blocchi = [
            andata1, ritorno1,
            andata2, ritorno2,
            andata3, ritorno3[:3]
        ]

        numero = 1

        for blocco in blocchi:
            for giornata in blocco:

                giornata_obj = Giornata.objects.create(
                    lega=lega,
                    giornata=numero
                )

                for casa, ospite in giornata:
                    PartitaLega.objects.create(
                        giornata=giornata_obj,
                        squadra_casa=casa,
                        squadra_ospite=ospite
                    )

                numero += 1

        lega.calendario_generato = True
        lega.save()

        self.stdout.write(self.style.SUCCESS("✔ Seed completato con successo!"))