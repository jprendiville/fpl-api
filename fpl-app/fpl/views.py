""" Module for Application views """

from django.shortcuts import render


def home(request):
    """ Respond to a request to display the home page """
    return render(request, 'home.html')

def denied_page(request):
    return render(request, 'denied-page.html')

def server_error(request):
    return render(request, 'server-error.html', status=500)
