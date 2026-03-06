from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Usage in template: {{ my_dict|get_item:key }}
    Allows dict lookup with a variable key in Django templates.
    """
    try:
        return dictionary.get(int(key), 0)
    except (ValueError, TypeError, AttributeError):
        return 0