# middleware.py
import traceback

from django.shortcuts import render

from fpl.properties.properties import get_properties
from manager.models import ClassicLeague

properties = get_properties()


class AccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for any exception
        response = self.get_response(request)

        # Check if the URL matches the specific pattern
        if '/managers/league/' in request.path_info and '/manager/' in request.path_info:
            try:
                path_parts = request.path_info.split('/')
                league_id_index = path_parts.index('league') + 1
                league_id = path_parts[league_id_index]

                manager_id_index = path_parts.index('manager') + 1
                manager_id = path_parts[manager_id_index]

                league = ClassicLeague.objects.get(league_id=league_id,
                                                   manager_id=manager_id)

                # 'x' represents a private league
                if league.league_type != 'x':
                    context = {}
                    context['message'] = properties.league_access_denied
                    return render(request, 'denied-page.html', context=context)
            except (ValueError, IndexError):
                # Handle the case where league_id or manager_id is not present in the URL
                context = {
                    'message': 'Invalid URL structure: league or manager not found'}
                return render(request, 'denied-page.html', context=context)
            except ClassicLeague.DoesNotExist:
                # Handle the case where the league with the specified league_id is not found
                context = {'message': 'Manager/League not found'}
                return render(request, 'denied-page.html', context=context)

        if response.status_code == 500:
            # Log the exception
            traceback.print_exc()
            context = {'message': 'Internal error, try again later'}
            return render(request, 'server-error.html', context=context)

        return response
