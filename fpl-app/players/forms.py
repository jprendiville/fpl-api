""" This module has a Modal Form to be used in the Player History modal
popup """

from bootstrap_modal_forms.forms import BSModalModelForm

from players.models import Player


class PlayerHistoryForm(BSModalModelForm):
    """ Modal popup for Player History """

    class Meta:
        """ Meta class to define the model and fields used for the
        modal """

        model = Player
        fields = ['id', 'total_points']


class PlayerPredictionHistoryForm(BSModalModelForm):
    """ Modal popup for Player History """

    class Meta:
        """ Meta class to define the model and fields used for the
        modal """

        model = Player
        fields = ['id', 'total_points']
