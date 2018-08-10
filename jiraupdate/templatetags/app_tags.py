from django import template

register = template.Library()

@register.assignment_tag
def count(page, itemnumber):
    
    result = (page - 1) * 10 + itemnumber

    return result

@register.assignment_tag
def convert(number):
    
    num = number
    
    return int(num)

@register.assignment_tag
def countloop(number):
    
    number = number +1
    
    return int(number)

@register.assignment_tag

def get_values(k, dic):

    if isinstance(dic,dict):
        return dic[k]
    else:
        return "something wrong"
