from .models import PartitaLega, Classifica, Squadra

def calcola_giornata(lega, giornata):
    if giornata.calcolata == True:
        return
    partite=PartitaLega.objects.filter(giornata=giornata)
    for partita in partite:
        partita.calcola_gol(lega=lega)
        
    for squadra in Squadra.objects.filter(lega=lega):
        classifica = Classifica.objects.get(squadra=squadra, lega=lega)
        classifica.risultati(lega=lega, giornata=giornata)

    giornata.calcolata = True
    giornata.save()