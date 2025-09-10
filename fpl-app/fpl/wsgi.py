"""
WSGI config for fpl project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from fpl.startup import startup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fpl.settings')

application = get_wsgi_application()
startup()
