from django_huey import get_queue
from huey.signals import SIGNAL_EXECUTING, SIGNAL_COMPLETE, SIGNAL_ERROR
from .. import models


task_queue = get_queue("tasks")


@task_queue.signal(SIGNAL_EXECUTING)
def task_is_started(signal, task):
    start_task(task)


@task_queue.signal(SIGNAL_COMPLETE)
def task_is_completed(signal, task):
    result = task_queue.result(task.id)
    task_complete(task, result)


@task_queue.signal(SIGNAL_ERROR)
def task_has_error(signal, task, exc):
    print(exc)
    task_error(task, exc)


def start_task(task):
    task_obj = models.HueyRelTask.objects.get(huey_id=task.id)
    task_obj.status = 'started'
    task_obj.save()


def task_complete(task, result):
    task_obj = models.HueyRelTask.objects.get(huey_id=task.id)
    task_obj.status = 'complete'
    task_obj.function.result = result
    task_obj.function.save()
    task_obj.save()


def task_error(task, message):
    task_obj = models.HueyRelTask.objects.get(huey_id=task.id)
    task_obj.status = 'error'
    task_obj.message = message
    task_obj.save()


def get_background_function_from_huey_id(huey_id):
    task = models.HueyRelTask.objects.get(huey_id=huey_id)
    function = task.function
    return function


def get_all_tasks(user):
    by_user = models.HueyRelTask.objects.filter(user=user)
    tasks = by_user.order_by("date_created")
    return tasks


def clear_all_tasks(user):
    by_user = models.HueyRelTask.objects.filter(user=user)
    running_tasks = by_user.filter(status='started')
    if len(running_tasks) > 0:
        raise RuntimeError('Tasks are currently running.')

    func_by_user = models.BackgroundFunction.objects.filter(hueyreltask__user=user)
    func_by_user.delete()
    by_user.delete()
    # func_by_user.delete()
