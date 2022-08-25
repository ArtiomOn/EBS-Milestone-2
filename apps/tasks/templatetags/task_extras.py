from django.template.loader_tags import register


@register.filter
def in_task(obj, task):
    return obj.filter(task=task)
