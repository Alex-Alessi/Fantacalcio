from django import forms
from .models import PARTECIPANTI_CHOICES, CREDITI_CHOICES

class LegaForm(forms.Form):
    name=forms.CharField(max_length=30)
    partecipanti=forms.ChoiceField(choices=PARTECIPANTI_CHOICES)
    password=forms.CharField(widget=forms.PasswordInput)
    crediti=forms.ChoiceField(choices=CREDITI_CHOICES)