import time
import uuid
from datetime import datetime
from django_huey import db_task
from .. import models


def create_new_add_two_numbers_error_task(a, b, user):
    obj_id = uuid.uuid4()
    date = datetime.now()
    task_obj = models.HueyRelTask(uuid=obj_id, date_created=date, user=user)
    func_obj = models.AddTwoNumbersError(first=a, second=b)
    func_obj.save()
    task_obj.function = func_obj
    task_obj.save()

    return task_obj


def get_add_two_numbers_error_task_list():
    tasks = models.HueyRelTask.objects.order_by("date_created")
    return tasks


@db_task(queue="tasks")
def add_numbers_error(a, b):
    time.sleep(5)
    sum = a + b
    if sum % 3 == 0:
        raise ValueError('Sum should not be a multiple of 3 >:(')
    if sum % 5 == 0:
        raise ValueError('Sum should not be a multiple of 5 :(')

    return sum


def do_add_numbers_error_task(a, b, user):
    task_db_obj = create_new_add_two_numbers_error_task(a, b, user)
    the_task = add_numbers_error(a, b)
    task_db_obj.huey_id = the_task.id
    task_db_obj.status = 'queued'
    task_db_obj.save()
    return task_db_obj
