from django import template

register = template.Library()


@register.filter
def class_errors(errors):
    return "is-invalid" if errors else ""
