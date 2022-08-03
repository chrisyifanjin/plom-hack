from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from . import services
from . import models
from . import forms
from . import ml

"""
TODO:
Create tasks in bulk (enqueue 100 tasks) (make me 100 PDFs for example)
Generate tasks, and then the user enqueueues them
Re-run tasks that fail
Re-build tasks in bulk
Cancel running tasks
Kill everything
Delete results of completed tasks
Try out many-to-one?
    - if so, we'd have history
    - otherwise, overwrite old task

Dummy PDFs
    - create 10 pdfs
    - process them in the background
    - view completed pdfs
    - handle error'd pdfs
"""


@login_required
def home_view(request):
    tasks = services.get_all_tasks(request.user)
    tasks_fragment = render_to_string('ml_huey/fragments/home_tasks_list.html', {'tasks': tasks})
    context = {
        'task_list': tasks_fragment,
        'add_form': forms.AddTwoNumbersForm,
        'gen_form': forms.NumberGuessForm
    }
    return render(request, 'ml_huey/index.html', context)


@login_required
def get_task_list(request):
    if request.method == 'GET':
        tasks = services.get_all_tasks(request.user)
        task_fragment = render_to_string('ml_huey/fragments/home_tasks_list.html', {'tasks': tasks})
        return HttpResponse(task_fragment)


@login_required
def create_add_task_view(request):
    if request.method == 'POST':
        post_data = request.POST
        print(post_data)
        first = int(post_data['first'])
        second = int(post_data['second'])
        user = request.user

        new_task = services.do_add_numbers_error_task(first, second, user)
        return HttpResponseRedirect(reverse("view_task", args=(new_task.uuid,)))


@login_required
def create_gen_task_view(request):
    if request.method == 'POST':
        post_data = request.POST
        if 'is_even_guess' in post_data.keys() and post_data['is_even_guess']:
            is_even = True
        else:
            is_even = False
        user = request.user

        new_task = services.do_gen_number_task(is_even, user)
        return HttpResponseRedirect(reverse("view_task", args=(new_task.uuid,)))


@login_required
def retry_gen_task_view(request, uuid):
    if request.method == 'POST':
        post_data = request.POST
        if 'is_even_guess' in post_data.keys() and post_data['is_even_guess']:
            is_even = True
        else:
            is_even = False
        user = request.user

        old_task = models.HueyRelTask.objects.get(uuid=uuid)
        background_function = old_task.function
        new_task = services.retry_gen_number_task(is_even, user, background_function)
        return HttpResponseRedirect(reverse("view_task", args=(new_task.uuid,)))


@login_required
def delete_tasks_view(request):
    if request.method == 'POST':
        try:
            user = request.user
            services.clear_all_tasks(user)
            return HttpResponseRedirect(reverse('get_tasks'))
        except RuntimeError:
            return HttpResponseRedirect(reverse('get_tasks'))


@login_required
def task_view(request, uuid):
    task = get_object_or_404(models.HueyRelTask, uuid=uuid)
    if type(task.function) == models.RandomNumberGen:
        retry_form = forms.NumberGuessForm
        context = {'task': task, 'retry_form': retry_form}
        results_fragment = render_to_string('ml_huey/fragments/task_status_results_gen.html', context, request=request)
    else:
        results_fragment = render_to_string('ml_huey/fragments/task_status_results_base.html', {'task': task}, request=request)

    args = task.function.args()
    desc = task.function.description()
    return render(request, 'ml_huey/task_view.html', {'task': task, 'description': desc, 'args': args, 'results': results_fragment})


@login_required
def get_task_status_view(request, uuid):
    task = get_object_or_404(models.HueyRelTask, uuid=uuid)
    results_fragment = render_to_string('ml_huey/fragments/task_status_results_base.html', {'task': task})
    if type(task.function) == models.RandomNumberGen:
        retry_form = forms.NumberGuessForm
        context = {'task': task, 'retry_form': retry_form}
        results_fragment = render_to_string('ml_huey/fragments/task_status_results_gen.html', context=context, request=request)
    else:
        results_fragment = render_to_string('ml_huey/fragments/task_status_results_base.html', {'task': task}, request=request)
    return HttpResponse(results_fragment)


@login_required
def get_task_status_ml_view(request):
    task = models.TrainMLModelTask.objects.all().last()
    endpt = task.knnmodelendpoint
    results_fragment = render_to_string('ml_huey/fragments/task_status_results_ml.html', {'task': task, 'endpt': endpt})
    return HttpResponse(results_fragment)


@login_required
def train_page_view(request):
    if request.method == 'GET':
        try:
            task = models.TrainMLModelTask.objects.all().last()
            endpoint = task.knnmodelendpoint
        except AttributeError:
            task = False
            endpoint = False

        results_fragment = render_to_string('ml_huey/fragments/task_status_results_ml.html', {'task': task, 'endpt': endpoint})
        return render(request, 'ml_huey/train_model.html', {'task': task, 'results': results_fragment})
    elif request.method == 'POST':
        print('Training model...')

        save_path = settings.MEDIA_ROOT / 'ml_huey'
        model_file = save_path / 'model.gzip'

        services.do_knn_train_sequence(3, str(model_file))
        return HttpResponseRedirect(reverse('train'))
