# Generated by Django 4.0.5 on 2022-06-09 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mocker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedpdf',
            name='pdf',
            field=models.FileField(upload_to='media/uploads'),
        ),
    ]
