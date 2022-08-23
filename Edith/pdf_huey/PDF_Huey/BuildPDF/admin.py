from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.BuildPDFTask)
admin.site.register(models.PDFDoc)
admin.site.register(models.PDFPage)
admin.site.register(models.HueyProcess)
