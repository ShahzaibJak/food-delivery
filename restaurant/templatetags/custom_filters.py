from django import template

register = template.Library()

@register.filter
def calculate_percentage(value, total):
    try:
        percentage = (float(value) / float(total)) * 100
        return round(percentage, 2)
    except (ValueError, ZeroDivisionError):
        return 0
