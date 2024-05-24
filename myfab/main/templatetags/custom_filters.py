from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def filter_choices_by_category(choices_list, category):
    return choices_list.filter(category=category)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def older_than_2_weeks(date):
    '''
    To check if the date is older than 2 weeks to dissable 
    return request button.
    '''
    if not date:
        return False
    two_weeks_ago = datetime.now().date() - timedelta(weeks=2)
    return date < two_weeks_ago