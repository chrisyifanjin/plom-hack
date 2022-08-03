from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.auth.models import User


class HueyTask(PolymorphicModel):
    """Store async function args/results in an inherited class"""
    # choices: todo, queued, started, done, error
    status = models.CharField(max_length=16, null=False, default='todo')
    huey_id = models.UUIDField(null=True)
    uuid = models.UUIDField(unique=True, null=True)
    date_created = models.DateTimeField(null=True)
    message = models.TextField(null=True)


class BackgroundFunction(PolymorphicModel):
    """Store the args and results of a background function"""
    pass


class HueyRelTask(models.Model):
    """Store async function args/results in a separate object"""
    # choices: todo, queued, started, done, error
    # call this background_function or something
    function = models.ForeignKey(BackgroundFunction, null=True, on_delete=models.SET_NULL, db_constraint=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_constraint=False)
    status = models.CharField(max_length=16, null=False, default='todo')
    huey_id = models.UUIDField(null=True)
    uuid = models.UUIDField(unique=True, null=True)
    date_created = models.DateTimeField(null=True)
    message = models.TextField(null=True)


class AddTwoNumbersTask(HueyTask):
    first = models.PositiveIntegerField(null=True)
    second = models.PositiveIntegerField(null=True)
    result = models.PositiveIntegerField(null=True)


class AddTwoNumbersErrorTask(HueyTask):
    first = models.PositiveIntegerField(null=True)
    second = models.PositiveIntegerField(null=True)
    result = models.PositiveIntegerField(null=True)


class AddTwoNumbersError(BackgroundFunction):
    first = models.PositiveIntegerField(null=True)
    second = models.PositiveIntegerField(null=True)
    result = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"{self.first} + {self.second}"

    def args(self):
        """Display the arguments in a nice way for template rendering"""
        return (
            f"""
            <div>
                <p>First: {self.first}</p>
                <p>Second: {self.second}</p>
            </div>
            """
        )

    def description(self):
        """A short text description for rendering."""
        return "Add two positive integers. If the result is a multiple of 3 or 5, raise an error!"


class RandomNumberGenTask(HueyTask):
    is_even_guess = models.BooleanField(default=False)
    result = models.PositiveIntegerField(null=True)


class RandomNumberGen(BackgroundFunction):
    is_even_guess = models.BooleanField(default=False)
    result = models.PositiveIntegerField(null=True)

    def __str__(self):
        if self.is_even_guess:
            return "Guess: even"
        else:
            return "Guess: odd"

    def args(self):
        """Display the arguments in a nice way for template rendering"""
        if self.is_even_guess:
            return "<p>Guess: even</p>"
        else:
            return "<p>Guess: odd</p>"

    def description(self):
        """A short text description for rendering"""
        return "Guess if a random number from 1 to 50 will be even. If you guess wrong, return an error!"


class TrainMLModelTask(HueyTask):
    pass


class KNNModelEndpoint(models.Model):
    train_task = models.OneToOneField(TrainMLModelTask, null=True, on_delete=models.SET_NULL)
    model_save_path = models.TextField(null=True)
    n_neighbors = models.PositiveIntegerField(null=True)
    train_acc = models.FloatField(null=True)
    test_acc = models.FloatField(null=True)
