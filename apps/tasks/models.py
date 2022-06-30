from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    status = models.BooleanField(default=False, verbose_name='Completed')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', null=True)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title
