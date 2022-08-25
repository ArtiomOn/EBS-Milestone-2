from django.template.loader_tags import register


@register.filter
def in_task(comment, task):
    return comment.filter(task=task)


@register.filter
def in_timelog(timelog, task):
    return timelog.filter(task=task)
