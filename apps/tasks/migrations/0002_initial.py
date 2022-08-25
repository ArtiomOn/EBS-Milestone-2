# Generated by Django 3.2.14 on 2022-08-25 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timelog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='time_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='task',
            name='assigned_to',
            field=models.ManyToManyField(related_name='tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='task',
            name='attachment',
            field=models.ManyToManyField(blank=True, related_name='task_attachments', to='tasks.Attachment'),
        ),
        migrations.AddField(
            model_name='task',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.task'),
        ),
        migrations.AddField(
            model_name='task',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.project'),
        ),
        migrations.AddField(
            model_name='project',
            name='logo',
            field=models.ManyToManyField(blank=True, to='tasks.Attachment'),
        ),
        migrations.AddField(
            model_name='project',
            name='member',
            field=models.ManyToManyField(blank=True, related_name='projects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='attachment',
            field=models.ManyToManyField(blank=True, related_name='comment_attachments', to='tasks.Attachment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tasks.task'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attachments', to=settings.AUTH_USER_MODEL),
        ),
    ]