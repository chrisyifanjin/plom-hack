from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from secrets import token_urlsafe

from . import forms
from . import services
from .models import UploadedPDF

"""
TODO: Manager can generate a one-time link for an un-authenticated user to upload
Keep track of open links
Max file size: 10MB
Capttcha code verification?
Instead of timestamp, find a convert to safe filename function

Other stuffs:
Poke around at CV stuff
Find QR code locations on page
Find answer boxes on page
Migrate digit code to sklearn? XGBoost? Pillow?
"""


class IndexView(TemplateView):
    template_name = 'mocker/index.html'


class SignupView(FormView):
    template_name = 'registration/create_user.html'
    form_class = forms.SignupForm
    success_url = '/'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        new_user = User.objects.create_user(username, email, password)
        login(self.request, new_user)
        return super().form_valid(form)


class BaseUploadView(FormView):
    template_name = 'mocker/upload.html'
    form_class = forms.PDFUploadForm
    pk = None

    def get_success_url(self):
        return reverse('mock', kwargs={'pk': self.pk})


class LoginUploadView(LoginRequiredMixin, BaseUploadView):
    def form_valid(self, form):
        user_id = self.request.user.id
        pdf = services.create_uploaded_pdf(user_id, False, self.request.FILES['pdf'])
        self.pk = pdf.pk
        return super().form_valid(form)


class GenerateLinkView(LoginRequiredMixin, TemplateView):
    template_name = 'mocker/linkgen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        token = token_urlsafe(nbytes=32)
        link = generate_link(token, 60, get_current_site(self.request))

        context['guest_link'] = link
        return context

    def generate_link(self, token, duration, link_prefix):
        if cache.get('guest_user_counter'):
            cache.incr('guest_user_counter')
        else:
            cache.set('guest_user_counter', 1, None)

        guest_userid = cache.get('guest_user_counter')
        cache.set(token, guest_userid, duration)

        link = f'{link_prefix}/upload/guest?token={token}'
        return link


class GuestUploadView(BaseUploadView):
    template_name = 'mocker/guest_upload.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('upload'))
        else:
            token = request.GET.get('token')
            if cache.get(token):
                return super().get(request, *args, **kwargs)
            else:
                raise PermissionDenied('Invalid guest link.')

    def form_valid(self, form):
        guest_id = cache.get(self.request.GET['token'])
        if not guest_id:
            raise PermissionDenied('Guest session has timed out.')
        print('Guest id:', guest_id)
        pdf = services.create_uploaded_pdf(guest_id, True, self.request.FILES['pdf'])
        self.pk = pdf.pk
        return super().form_valid(form)


def pdf_convert(request, pk):
    pdf = get_object_or_404(UploadedPDF, pk=pk)

    try:
        mock_exam = services.create_mock_exam(pdf, 'Plom exam - DRAFT')
        response =  HttpResponse(mock_exam.convert_to_pdf())

        filename_slug = pdf.filename_slug
        save_filename = 'plom-mock-exam-' + filename_slug + '.pdf'

        response['Content-Disposition'] = f"attachment; filename={save_filename}"
        return response
    except services.ExamBuildException:
        services.delete_uploaded_pdf(pdf)
        return HttpResponse("Error when building mock exam PDF", status=500)


def generate_link(request):
    inviter = request.user.username
    token = token_urlsafe(nbytes=32)
    link = str(get_current_site(request)) + reverse('guest_upload', args=(token,))
    return HttpResponse(link)


def guest_upload(request, token):
    return HttpResponse('Welcome, Guest!')
