from django import template

register = template.Library()


@register.filter
def isinstance_of(value, class_name):
    return isinstance(value, class_name)
