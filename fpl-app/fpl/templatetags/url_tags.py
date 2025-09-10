""" Module for Template Tags """

from django import template

register = template.Library()


@register.simple_tag
def this_url(value, field_name, urlencode=None):
    """ Parses parameters in a url

    Example url is page=
    The below code is to allow for multiple filters.
    In the first iteration only element_type will be available
    :param value: page number
    :param field_name: string page
    :param urlencode: part of the url from <page> to the end of the url
    """
    url = f'?{field_name}={value}'

    if urlencode:
        # Split the url elements by & into a list
        querystring = urlencode.split('&')

        # Now make a filter query string, exluding field_name (ie, the page
        # part of the url)  eg. ['page=2', 'parm2'] will go to ['param=parm2']
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)

        # Concatenate together the filter_querystring elements
        encoded_querystring = '&'.join(filtered_querystring)

        # Reformat the url as ?page=2&param=parm2
        url = f'{url}&{encoded_querystring}'

    return url
