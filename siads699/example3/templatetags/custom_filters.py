import json
from django import template

register = template.Library()

@register.filter(name='nested_json_dict')
def nested_json_dict_get(value, arg):
    try:
        data = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None

    keys = arg.split('.')
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(data):
                data = data[idx]
            else:
                return None
        else:
            return None
    return data