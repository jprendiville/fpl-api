""" Module ordering a queryset """

from django import template

register = template.Library()


@register.filter
def sort_by(queryset, order):
    """ Sort a query set by the given order """
    return queryset.order_by(order)
