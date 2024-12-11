from django import template

register = template.Library()

@register.filter
def format_large_number(value):
    if not value:
        return '-'
    
    try:
        value = float(value)
        if abs(value) >= 1e9:
            return f"{value/1e9:.3f}B"
        elif abs(value) >= 1e6:
            return f"{value/1e6:.3f}M"
        return f"{value:,.0f}"
    except (ValueError, TypeError):
        return '-'

@register.filter
def format_currency(value):
    if not value:
        return '-'
    
    try:
        value = float(value)
        if abs(value) >= 1e9:
            return f"${value/1e9:.3f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.3f}M"
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return '-' 