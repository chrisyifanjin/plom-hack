from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.HueyRelTask)
admin.site.register(models.AddTwoNumbersError)
admin.site.register(models.RandomNumberGen)
admin.site.register(models.TrainMLModelTask)
admin.site.register(models.KNNModelEndpoint)
