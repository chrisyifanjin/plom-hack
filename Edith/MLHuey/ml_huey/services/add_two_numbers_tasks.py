import time
import uuid
from datetime import datetime
from django_huey import db_task
from .. import models


def create_new_add_two_numbers_task():
    obj_id = uuid.uuid4()
    date = datetime.now()
    task_obj = models.AddTwoNumbersTask(uuid=obj_id, date_created=date)
    task_obj.save()

    return task_obj


def get_add_two_numbers_task_list():
    tasks = models.AddTwoNumbersTask.objects.order_by("date_created")
    return tasks


@db_task(queue="tasks")
def add_numbers(a, b, obj_id):
    time.sleep(5)
    sum = a + b
    task_obj = models.AddTwoNumbersTask.objects.get(uuid=obj_id)
    task_obj.result = sum
    task_obj.save()
    return sum


def do_add_numbers_task(a, b):
    task_db_obj = create_new_add_two_numbers_task()
    the_task = add_numbers(a, b, task_db_obj.uuid)
    task_db_obj.huey_id = the_task.id
    task_db_obj.status = 'queued'
    task_db_obj.first = a
    task_db_obj.second = b
    task_db_obj.save()
    return task_db_obj
