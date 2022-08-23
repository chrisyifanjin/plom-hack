import pathlib
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from polymorphic.models import PolymorphicModel
from . import services


class PDFDoc(models.Model):
    """A PDF document. Contains a pre-determined number of pages."""
    num_pages = models.PositiveIntegerField(default=0)
    save_path = models.TextField(default="")
    nice_name = models.TextField(default="")


@receiver(pre_delete, sender=PDFDoc)
def clear_pdf(sender, instance, **kwargs):
    """When a PDFDoc model is deleted, also delete the PDF file on disk"""
    file_path = pathlib.Path(instance.save_path)
    if file_path.exists() and file_path.is_file():
        file_path.unlink()


class PDFPage(models.Model):
    """A page in a PDF file. It contains a string of text to display."""
    display_string = models.TextField(default="")
    pdf_doc = models.ForeignKey(PDFDoc, on_delete=models.CASCADE, null=True)
    zero_index = models.PositiveIntegerField(default=0)


class HueyProcess(models.Model):
    """Wrapper for an ongoing Huey task"""
    huey_id = models.UUIDField(null=True)
    # options: todo, queued, started, done, error
    status = models.CharField(max_length=20, default='todo')
    date_created = models.DateTimeField(null=True)
    message = models.TextField(null=True)


class BackgroundTask(PolymorphicModel):
    """Base class for any tasks that run in the background"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    task_id = models.UUIDField(null=True)
    huey_process = models.OneToOneField(HueyProcess, on_delete=models.SET_NULL, null=True)


class BuildPDFTask(BackgroundTask):
    """Class for building PDFs in the background"""
    pdf_doc = models.OneToOneField(PDFDoc, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Build PDF: {self.pdf_doc.nice_name}"

    def start(self):
        services.start_build_task(self)

    def retry(self):
        services.retry_build_task(self)

    def cancel_todo(self):
        services.cancel_todo_build_task(self)
