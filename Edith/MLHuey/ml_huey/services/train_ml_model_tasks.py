import queue
import time
import uuid
from datetime import datetime
from django_huey import db_task
from .. import models
from .. import ml


def create_ml_train_task():
    """Create a huey task object for training a model, and an associated endpoint object"""
    obj_id = uuid.uuid4()
    date = datetime.now()
    task_obj = models.TrainMLModelTask(uuid=obj_id, date_created=date)
    task_obj.save()

    endpoint_obj = models.KNNModelEndpoint(train_task=task_obj)
    endpoint_obj.save()

    return task_obj, endpoint_obj


@db_task(queue="tasks")
def run_knn_train_sequence(n, save_filepath, endpoint):
    """Submit a training sequence to the queue"""
    train_acc = ml.train_knn_classifier(n, save_filepath)
    endpoint.train_acc = train_acc
    endpoint.save()
    return True


def do_knn_train_sequence(n, save_filepath):
    """Train a KNN model"""
    task_obj, endpoint = create_ml_train_task()
    the_task = run_knn_train_sequence(n, save_filepath, endpoint)
    task_obj.huey_id = the_task.id
    task_obj.status = 'queued'
    endpoint.n_neighbors = n
    endpoint.model_save_path = save_filepath
    task_obj.save()
    endpoint.save()
    print(endpoint.n_neighbors)
    return task_obj, endpoint
