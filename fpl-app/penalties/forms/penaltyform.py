""" This module has a class ModelForm for creating a penalty """

from django import forms
from django_filters import ModelChoiceFilter

from common.models.event import Event
from ..models import penalty


class CreatePenalty(forms.ModelForm):
    """ Form to create and save a penalty """
    gameweek = ModelChoiceFilter(queryset=Event.objects.filter(finished=True)
                                 .order_by('-id'), label='Select Gameweek')

    class Meta:
        """ Meta class to define the model and fields used for the form """

        model = penalty.Penalty
        fields = ["gameweek", "team", "taker", "goalkeeper",
                  "venue", "result", "var_awarded"]
