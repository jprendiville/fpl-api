from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.contrib import messages
from queue import Queue

from fpl.dataloader.load.fpl_data import load_and_save_fpl_data, \
    load_and_save_player_data
from fpl.dataloader.load.load_managers import manager_picks_notok
from fpl.exceptions.fpl_data_exceptions import FplDataError, FplPlayerDataError
from players.models import PlayerStatus
from utils.message_utils import add_message, properties
from utils.rebuild_predictions import rebuild_predictions


def refresh_all_data(request):
    """ Respond to a request to reload data from the FPL api """

    result_queue = Queue()
    try:
        load_and_save_fpl_data(True, result_queue)
    except FplDataError:
        messages.error(*add_message(request, 'Failed to retrieve FPL data', None))
        return redirect('home')
    except FplPlayerDataError:
        while not result_queue.empty():
            team_name, error = result_queue.get()
            if error:
                messages.error(*add_message(request, f'Failed to retrieve FPL player data for {team_name}', properties.message_short_timeout))
        messages.error(*add_message(request, 'Failed to retrieve all FPL player data', None))
        return redirect('home')

    if manager_picks_notok():
        messages.error(*add_message(request, 'Data refreshed, but some data missing for managers!', None))
    else:
        messages.success(*add_message(request, 'Data has been refreshed successfully!', None))
    return redirect('home')


def refresh_player_data(request):
    result_queue = Queue()
    try:
        load_and_save_player_data(True, result_queue)
    except FplDataError:
        messages.error(*add_message(request, 'Failed to retrieve FPL data', None))
        return redirect('home')
    except FplPlayerDataError:
        while not result_queue.empty():
            team_name, error = result_queue.get()
            if error:
                messages.error(*add_message(request, f'Failed to retrieve FPL player data for {team_name}', properties.message_short_timeout))
        messages.error(*add_message(request, 'Failed to retrieve all FPL player data', None))
        return redirect('home')

    messages.success(*add_message(request, 'Player data has been refreshed successfully!', None))
    return redirect('home')


def recalculate_predictions(request, recalculate_all=False):
    try:
        rebuild_predictions(True, recalculate_all)
    except:
        messages.error(*add_message(request, 'Error rebuilding predictions'))
        return redirect('home')

    messages.success(*add_message(request, 'Predictions rebuilt'))
    return redirect('predictions')
