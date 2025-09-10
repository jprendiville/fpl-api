from fpl.properties.properties import get_properties

properties = get_properties()

def add_message(request, message_text, delay_time=None):

    if not delay_time:
        delay_time = properties.message_timeout
    extra_tags = str(delay_time)

    return request, message_text, extra_tags