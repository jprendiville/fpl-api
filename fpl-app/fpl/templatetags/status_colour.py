""" Module for Player Status styling """

from django import template

register = template.Library()


@register.simple_tag
def get_message_css_status(status):
    """ Returns the class name for a tag based on the player status """
    match status:
        case 'i':
            return 'status-injured'
        case 'a':
            return 'status-available'
        case 'd':
            return 'status-partial-injured'
        case 'u':
            return 'status-transferred'
        case 's' | 'n':
            return 'status-unavailable'
        case _:
            return 'status-unknown'
