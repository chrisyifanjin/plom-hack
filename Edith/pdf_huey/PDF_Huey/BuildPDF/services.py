import pathlib
import uuid
import random
import lorem
import fitz
from django_huey import get_queue, db_task
from huey.signals import SIGNAL_EXECUTING, SIGNAL_COMPLETE, SIGNAL_ERROR
from datetime import datetime
from django.conf import settings
from django.db import transaction
from . import models


@db_task(queue="tasks")
@transaction.atomic()
def build_a_pdf(pdf_doc, user):
    """Build a PDF, fill pages with placeholder text, and save to database/disk
    
    Returns:
        models.PDFDoc: the built PDF database object
    """

    if pdf_doc.num_pages <= 10:
        raise ValueError('Error when PDF is 10 pages or less!')

    for i in range(pdf_doc.num_pages):
        display_string = '\n'.join(lorem.paragraph().split('. '))
        pdf_page = models.PDFPage(zero_index=i, display_string=display_string, pdf_doc=pdf_doc)
        pdf_page.save()

    _build_a_pdf(pdf_doc)

    return pdf_doc


@transaction.atomic()
def _build_a_pdf(pdf_doc):
    """Create a fitz PDF document, fill its pages with text, and save to disk"""
    with fitz.open() as fitz_doc:
        for i in range(pdf_doc.num_pages):
            try:
                page = pdf_doc.pdfpage_set.get(zero_index=i)
            except:
                raise ValueError(pdf_doc.pdfpage_set)
            fitz_doc.insert_page(-1, text=page.display_string)

        save_path = pathlib.Path(pdf_doc.save_path)
        fitz_doc.save(save_path)


@transaction.atomic()
def create_build_task(user, pdf_task=None):
    """Initialize a PDF building task (but don't submit yet)"""
    if not pdf_task:
        pdf_task = models.BuildPDFTask(task_id=uuid.uuid4(), user=user)
    pdf_doc = models.PDFDoc()

    user_folder = settings.MEDIA_ROOT / user.username
    if not user_folder.exists():
        user_folder.mkdir()

    filename = str(uuid.uuid4()) + '.pdf'
    save_path = user_folder / filename
    pdf_doc.save_path = save_path

    n_pages = random.randint(1, 50)        
    pdf_doc.num_pages = n_pages

    pdf_doc.save()

    nice_filename = f"{user.username}_{n_pages}_{pdf_doc.pk}.pdf"
    pdf_doc.nice_name = nice_filename

    pdf_doc.save()

    pdf_task.pdf_doc = pdf_doc
    pdf_task.save()
    return pdf_task


@transaction.atomic()
def start_build_task(build_task):
    """Send a PDF build task to Huey"""
    huey_process = models.HueyProcess(date_created=datetime.now())
    pdf_doc = build_task.pdf_doc
    user = build_task.user

    background_task = build_a_pdf(pdf_doc, user)
    huey_process.huey_id = background_task.id
    huey_process.status = 'queued'
    huey_process.save()

    build_task.huey_process = huey_process
    build_task.save()


@transaction.atomic()
def retry_build_task(build_task):
    """Retry building a PDF"""
    old_huey = build_task.huey_process
    old_pdf = build_task.pdf_doc

    build_task.huey_process = None
    build_task.pdf_doc = None

    old_huey.delete()
    old_pdf.delete()

    new_task = create_build_task(build_task.user, build_task)
    start_build_task(new_task)


# @transaction.atomic(durable=True)
# def retry_build_task(build_task):
#     """Retry building a PDF"""
#     huey_process = models.HueyProcess(date_created=datetime.now())
#     background_task = build_a_pdf(build_task.pdf_doc, build_task.user)
#     huey_process.huey_id = background_task.id
#     huey_process.status = 'queued'
#     huey_process.save()


def list_tasks_for_a_user(user):
    """Get all of the tasks submitted by a user"""
    build_pdf_tasks = models.BuildPDFTask.objects.filter(user=user)
    ordered = build_pdf_tasks.order_by('huey_process__date_created')
    return ordered


@transaction.atomic()
def cancel_todo_build_task(build_task):
    """Cancel a BuildTask before it has been sent to Huey"""
    build_task.pdf_doc.delete()
    build_task.delete()


@transaction.atomic()
def cancel_queued_build_task(build_task):
    """Cancel a BuildTask after it's been sent to Huey"""
    huey_queue = get_queue("tasks")
    huey_id = build_task.huey_process.huey_id
    res = huey_queue.get(huey_id)
    res.revoke()

    # for now, don't worry about resuming tasks
    build_task.pdf_doc.delete()
    build_task.huey_process.delete()
    build_task.delete()


"""
Huey stuff
"""

task_queue = get_queue("tasks")

@task_queue.signal(SIGNAL_EXECUTING)
def start_task(signal, task):
    huey_obj = models.HueyProcess.objects.get(huey_id=task.id)
    huey_obj.status = 'started'
    huey_obj.save()


@task_queue.signal(SIGNAL_COMPLETE)
def end_task(signal, task):
    huey_obj = models.HueyProcess.objects.get(huey_id=task.id)
    huey_obj.status = 'complete'
    huey_obj.save()


@task_queue.signal(SIGNAL_ERROR)
def error_task(signal, task, exc):
    huey_obj = models.HueyProcess.objects.get(huey_id=task.id)
    huey_obj.status = 'error'
    huey_obj.message = exc
    huey_obj.save()

