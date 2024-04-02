from django import template
import os

register = template.Library()


@register.filter
def filename(value):
    return os.path.basename(value)


@register.filter
def filesize(value):
    value = int(value)
    if value < 1024:
        return f'{value} B'
    elif value < 1024 * 1024:
        return f'{value / 1024:.2f} KB'
    elif value < 1024 * 1024 * 1024:
        return f'{value / 1024 / 1024:.2f} MB'
    else:
        return f'{value / 1024 / 1024 / 1024:.2f} GB'


@register.filter
def extension(value):
    return os.path.splitext(value)[1][1:]
