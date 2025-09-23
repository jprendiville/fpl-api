# middleware.py
import traceback
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from fpl.properties.properties import get_properties
from manager.models import ClassicLeague

properties = get_properties()

def _is_api_request(request: HttpRequest) -> bool:
    # Keep it simple: everything under /api/ is API.
    # (Optionally also check Accept header for application/json.)
    return (request.path_info or "").startswith("/api/")

class AccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        is_api = _is_api_request(request)

        # ---------- PRE-VIEW: only gate HTML pages ----------
        if (not is_api) and ('/managers/league/' in request.path_info and '/manager/' in request.path_info):
            try:
                parts = [p for p in request.path_info.split('/') if p]  # remove empties
                league_id = parts[parts.index('league') + 1]
                manager_id = parts[parts.index('manager') + 1]

                league = ClassicLeague.objects.get(league_id=league_id, manager_id=manager_id)

                # 'x' = private league? deny access to non-private (keep your logic)
                if league.league_type != 'x':
                    return render(request, 'denied-page.html',
                                  context={'message': properties.league_access_denied},
                                  status=403)
            except (ValueError, IndexError, ClassicLeague.DoesNotExist):
                return render(request, 'denied-page.html',
                              context={'message': 'Manager/League not found or invalid URL'},
                              status=404)

        # ---------- CALL VIEW ----------
        try:
            response = self.get_response(request)
        except Exception:
            # For API: let DRF handle & format JSON errors
            if is_api:
                raise
            # For HTML: show your server error page
            traceback.print_exc()
            return render(request, 'server-error.html',
                          context={'message': 'Internal error, try again later'},
                          status=500)

        # ---------- POST-VIEW: turn 5xx into HTML *only* for non-API ----------
        if (not is_api) and response.status_code >= 500:
            return render(request, 'server-error.html',
                          context={'message': 'Internal error, try again later'},
                          status=500)

        return response
