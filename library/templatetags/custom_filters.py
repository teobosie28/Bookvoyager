from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def highlight_search(text, query):
    if not query:
        return text
    pattern = re.compile(f'({re.escape(query)})', re.IGNORECASE)
    return mark_safe(pattern.sub(r'<span class="highlight">\1</span>', text))

@register.filter
def truncate_words(text, length=50):
    words = text.split()
    if len(words) <= length:
        return text
    return ' '.join(words[:length]) + '...' 