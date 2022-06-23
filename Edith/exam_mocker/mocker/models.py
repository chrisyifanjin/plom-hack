import re
from django.db import models
from django.utils.text import slugify


def user_path(instance, filename):
    if instance.is_guest_upload:
        new_path = f"media/guest{instance.user_id}/{slugify(re.sub('.pdf$', '', filename))}.pdf"
    else:
        new_path = f"media/user{instance.user_id}/{slugify(re.sub('.pdf$', '', filename))}.pdf"
    print(new_path)
    return new_path

class UploadedPDF(models.Model):
    filename_slug = models.CharField(max_length=100, default='')
    is_guest_upload = models.BooleanField(default=True)
    user_id = models.IntegerField(default=0)
    pdf = models.FileField(upload_to=user_path)