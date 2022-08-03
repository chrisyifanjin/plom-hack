import uuid
from django.test import TestCase
from model_bakery import baker

from . import services
from . import models


class HueyTasksTests(TestCase):
    def test_get_function_by_huey_id(self):
        """Test services.get_function_from_huey_id"""
        func = baker.make(models.BackgroundFunction)
        task = baker.make(models.HueyRelTask, huey_id=uuid.uuid4(), function=func)
        huey_id = task.huey_id
        
        func_ref = services.get_background_function_from_huey_id(huey_id)
        self.assertEqual(func_ref, func)

    def test_get_function_by_huey_id_many(self):
        """Test services.get_function_from_huey_id with more than one database item"""
        func1 = baker.make(models.BackgroundFunction)
        func2 = baker.make(models.BackgroundFunction)
        task1 = baker.make(models.HueyRelTask, huey_id=uuid.uuid4(), function=func1)
        task2 = baker.make(models.HueyRelTask, huey_id=uuid.uuid4(), function=func2)

        func_ref = services.get_background_function_from_huey_id(task1.huey_id)
        self.assertEqual(func_ref, func1)
