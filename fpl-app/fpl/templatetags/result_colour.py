""" Module for Player Status styling """

from django import template

register = template.Library()


@register.simple_tag
def get_result_css_status(result):
    """ Returns the class name for a tag based on the game result """
    return result
