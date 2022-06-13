from urllib import response
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')


class ManageView(View):
    def get(self, request):
        return render(request, 'manage.html')


class MarkView(View):
    def get(self, request):
        return render(request, 'mark.html')

class ScanView(View):
    def get(self, request):
        return render(request, 'scan.html')
