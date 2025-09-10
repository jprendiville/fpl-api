from django import template

register = template.Library()


@register.simple_tag
def get_gameweek_points(manager_team, gameweek):
    return manager_team.get_gameweek_live_points(gameweek)

@register.simple_tag
def get_total_points(manager_team, gameweek, this_league):
    return manager_team.get_total_live_points(gameweek, this_league)

@register.simple_tag
def get_player_live_points(pick, gameweek):
    return pick.get_live_points(gameweek)

@register.simple_tag(takes_context=True)
def set_html_variable(context, name, value):
    context[name] = value
    return ''