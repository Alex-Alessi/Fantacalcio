from .models import PartitaLega, Classifica, Squadra

def calcola_giornata(lega, giornata):
    if giornata.calcolata:
        return
    
    partite=PartitaLega.objects.filter(giornata=giornata)

    for partita in partite:
        partita.calcola_gol(lega=lega)
        
    squadre = Squadra.objects.filter(lega=lega)

    for squadra in squadre:
        classifica, _ = Classifica.objects.get_or_create(
            squadra=squadra,
            lega=lega
        )

        classifica.risultati(lega=lega, giornata=giornata)

    giornata.calcolata = True
    giornata.save()