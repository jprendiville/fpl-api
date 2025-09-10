""" Configuration for test suites """

import os
import sys

import django
import pytest
from django.test import Client

sys.path.append(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def django_db_setup():
    """ Run the Django db setup for the test suite """
    django.setup()


@pytest.fixture
def client():
    """ Define a Django test client for the test suite """
    test_client = Client()
    return test_client
