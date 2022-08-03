# Generated by Django 4.0.6 on 2022-08-03 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ml_huey', '0003_remove_hueyreltask_function_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backgroundfunction',
            name='huey_task',
        ),
        migrations.RemoveField(
            model_name='backgroundfunction',
            name='user',
        ),
        migrations.AddField(
            model_name='hueyreltask',
            name='function',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ml_huey.backgroundfunction'),
        ),
        migrations.AddField(
            model_name='hueyreltask',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
