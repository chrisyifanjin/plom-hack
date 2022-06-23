from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission


def create_groups(apps, schema_editor):
    group_names = ['Manager', 'Scanner', 'Marker']
    for name in group_names:
        Group.objects.create(name=name)

    # create and apply permissions
    for app_config in apps.get_app_config():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None
