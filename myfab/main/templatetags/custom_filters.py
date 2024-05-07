from django import template
from main.models import CategoryChoice 

register = template.Library()

@register.filter
def filter_choices_by_category(choices_list, category):
    return choices_list.filter(category=category)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)