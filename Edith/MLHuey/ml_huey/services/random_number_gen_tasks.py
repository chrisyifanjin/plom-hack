import time
import random
import uuid
from datetime import datetime
from django_huey import db_task
from .. import models


def create_new_gen_number_task(is_even_guess, user, func_obj=None):
    obj_id = uuid.uuid4()
    date = datetime.now()
    task_obj = models.HueyRelTask(uuid=obj_id, date_created=date, user=user)

    if not func_obj:
        func_obj = models.RandomNumberGen(is_even_guess=is_even_guess)
        func_obj.save()
    else:
        func_obj.is_even_guess = is_even_guess
        func_obj.save()

    task_obj.function = func_obj
    task_obj.save()

    return task_obj


@db_task(queue="tasks")
def gen_random_number(is_even_guess):
    time.sleep(5)
    roll = random.randint(1, 50)
    if roll % 2 == 0 and is_even_guess:
        return roll
    elif roll % 2 == 1 and not is_even_guess:
        return roll

    raise RuntimeError(f'Darn! You guessed wrong. The number is {roll}')


def do_gen_number_task(is_even_guess, user):
    task_db_obj = create_new_gen_number_task(is_even_guess, user)
    the_task = gen_random_number(is_even_guess)
    task_db_obj.huey_id = the_task.id
    task_db_obj.status = 'queued'
    task_db_obj.save()
    return task_db_obj


def retry_gen_number_task(is_even_guess, user, background_func):
    task_db_obj = create_new_gen_number_task(is_even_guess, user, background_func)
    the_task = gen_random_number(is_even_guess)
    task_db_obj.huey_id = the_task.id
    task_db_obj.status = 'queued'
    task_db_obj.save()
    return task_db_obj