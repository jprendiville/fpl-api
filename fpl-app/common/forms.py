""" This module has a Modal Form to be used in the Player History modal
popup """

from django import forms
from django.forms import ModelChoiceField

from common.models.event import Event


class GameweekForm(forms.Form):
    gameweek = ModelChoiceField(
        queryset=Event.objects.filter(finished=True).order_by('-id'),
        required=False,
        label='FPL Gameweek',
        widget=forms.Select(attrs={'onchange': 'this.form.submit();'})
    )

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
