""" Module for Penalty views """

from django.core.paginator import Paginator
from django.db.models import Case, Count, Value, When
from django.shortcuts import redirect, render

from fpl.properties.properties import get_properties
from penalties.models.penalty import Penalty
from .filters import PenaltyFilter
from .forms import penaltyform

properties = get_properties()


def penalties(request):
    """ Respond to a request to display Penalties """
    context = {}

    # Get all the penalties and totals
    penalties = PenaltyFilter(queryset=Penalty.objects.all().order_by('-gameweek'))
    penalty_totals = Penalty.objects.aggregate(total_awarded=Count('id'),
                                               total_home=Count(Case(When(venue=Penalty.Venue.HOME, then=Value(1)))),
                                               total_away=Count(Case(When(venue=Penalty.Venue.AWAY, then=Value(1)))),
                                               total_scored=Count(
                                                   Case(When(result=Penalty.Result.SCORED, then=Value(1)))),
                                               total_missed=Count(
                                                   Case(When(result=Penalty.Result.MISSED, then=Value(1)))),
                                               total_saved=Count(
                                                   Case(When(result=Penalty.Result.SAVED, then=Value(1)))),
                                               total_var_awarded=Count(Case(When(var_awarded=True, then=Value(1)))),
                                               total_success_percent=Count(Case(
                                                   When(result=Penalty.Result.SCORED, then=Value(1)))) * 100 / Count(
                                                   'id'),
                                               total_var_percent=Count(
                                                   Case(When(var_awarded=True, then=Value(1)))) * 100 / Count('id'))

    context['penalties'] = penalties
    context['penalty_totals'] = penalty_totals

    # Get this page
    paginated_penalties = Paginator(penalties.qs, properties.page_size)
    page_number = request.GET.get('page')
    penalties_page_obj = paginated_penalties.get_page(page_number)
    context['penalty_page_obj'] = penalties_page_obj

    return render(request, 'penalties.html', context=context)


def penalty_create(request):
    """ Respond to a request to Create a new penalty """
    if request.method == 'POST':
        penalty_form = penaltyform.CreatePenalty(request.POST)
        if penalty_form.is_valid():
            penalty_form.save()
            return redirect('penalties')
    else:
        penalty_form = penaltyform.CreatePenalty()
    return render(request, 'create.html', {'penalty_form': penalty_form})
