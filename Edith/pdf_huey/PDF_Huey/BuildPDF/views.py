import pathlib
from urllib import request
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from . import forms
from . import services
from . import models


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'BuildPDF/index.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['form'] = forms.BuildPDFsForm

        tasks = services.list_tasks_for_a_user(self.request.user)
        tasks_fragment = render_to_string('BuildPDF/fragments/pdf_tasks.html', {'tasks': tasks})
        context['fragment'] = tasks_fragment

        return context

    def post(self, request):
        post_data = request.POST
        n_pdfs = int(post_data['num_pdfs'])
        for i in range(n_pdfs):
            task = services.create_build_task(request.user)
        return HttpResponseRedirect(reverse('index'))


class TaskListUtilView(LoginRequiredMixin, View):
    """Base class for views that update the task list"""

    def get_new_list_fragment(self, user):
        """Return an HTML fragment of the new task list"""
        tasks = services.list_tasks_for_a_user(user)
        tasks_fragment = render_to_string('BuildPDF/fragments/pdf_tasks.html', {'tasks': tasks})
        return tasks_fragment


class CreateTasks(TaskListUtilView):
    def post(self, request):
        """Create n PDF tasks"""
        post_data = request.POST
        n_pdfs = int(post_data['num_pdfs'])
        for i in range(n_pdfs):
            task = services.create_build_task(request.user)

        fragment = self.get_new_list_fragment(request.user)
        return HttpResponse(fragment)


class StartTask(TaskListUtilView):
    def post(self, request, task_id):
        """Start a background task, init huey process"""
        task = get_object_or_404(models.BackgroundTask, task_id=task_id)

        if task.user != request.user:
            raise PermissionDenied()

        if not task.huey_process:
            task.start()

        fragment = self.get_new_list_fragment(request.user)
        return HttpResponse(fragment)


class CancelTask(TaskListUtilView):
    def post(self, request, task_id):
        """Cancel background task"""
        task = get_object_or_404(models.BackgroundTask, task_id=task_id)

        if task.user != request.user:
            raise PermissionDenied()

        if not task.huey_process:
            task.cancel_todo()

        fragment = self.get_new_list_fragment(request.user)
        return HttpResponse(fragment)


class RetryTask(TaskListUtilView):
    def post(self, request, task_id):
        """Retry a background task"""
        task = get_object_or_404(models.BackgroundTask, task_id=task_id)

        if task.user != request.user:
            raise PermissionDenied()

        task.retry()

        fragment = self.get_new_list_fragment(request.user)
        return HttpResponse(fragment)


class Refresh(TaskListUtilView):
    def get(self, request):
        """Show all of the user's tasks"""
        fragment = self.get_new_list_fragment(request.user)
        return HttpResponse(fragment)


class StartAll(TaskListUtilView):
    def post(self, request):
        """Start all of the todo tasks"""
        tasks = services.list_tasks_for_a_user(request.user)
        for t in tasks:
            if not t.huey_process:
                t.start()

        fragment = self.get_new_list_fragment(request.user)
        return HttpResponse(fragment)


class RetryAll(TaskListUtilView):
    def post(self, request):
        """Retry all of the tasks that raised errors"""
        error_tasks = models.BackgroundTask.objects.filter(user=request.user, huey_process__status='error')
        for t in error_tasks:
            t.retry()

        fragment = self.get_new_list_fragment(request.user)
        return HttpResponse(fragment)


class ClearEverything(TaskListUtilView):
    """For debugging: clear everything from the queue and database!"""
    def post(self, request):
        currently_running = models.HueyProcess.objects.filter(status='started')
        if len(currently_running) == 0:
            user = request.user
            models.HueyProcess.objects.filter(backgroundtask__user=user).delete()
            models.PDFDoc.objects.filter(buildpdftask__user=user).delete()
            models.BackgroundTask.objects.filter(user=user).delete()
        
        fragment = self.get_new_list_fragment(request.user)
        return HttpResponse(fragment)


class GetPDF(LoginRequiredMixin, View):
    def get(self, request, task_id):
        """Return a built PDF"""
        task = get_object_or_404(models.BuildPDFTask, task_id=task_id)
        
        if task.user != request.user:
            raise PermissionDenied()

        if not task.pdf_doc:
            return HttpResponse(status=500)

        pdf_path = pathlib.Path(task.pdf_doc.save_path)
        if not pdf_path.exists() or not pdf_path.is_file():
            return HttpResponse(status=500)

        file = pdf_path.open('rb')
        return FileResponse(file)
