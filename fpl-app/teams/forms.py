""" This module has a Modal Form to be used in the Player History modal
popup """

from django import forms
from django.forms import DateField, HiddenInput, ModelChoiceField

from common.models.event import Event


class LeagueTableForm(forms.Form):
    gameweek = ModelChoiceField(
        queryset=Event.objects.filter(finished=True).order_by('-id'),
        required=False,
        label='FPL Gameweek',
        widget=forms.Select(attrs={'onchange': 'this.form.submit();'})
    )
    event_date = DateField(
        required=False,
        label='Date',
        widget=forms.DateInput(attrs={'type': 'date', 'onchange': 'this.form.submit();'})
    )
    last_field_changed = forms.CharField(widget=HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        last_field_changed = cleaned_data.get('last_field_changed')

        if last_field_changed == 'gameweek':
            cleaned_data['event_date'] = None
        elif last_field_changed == 'event_date':
            cleaned_data['gameweek'] = None

        return cleaned_data
