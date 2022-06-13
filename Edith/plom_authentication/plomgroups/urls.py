from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('manage/', views.ManageView.as_view(), name="manage"),
    path('scan/', views.ScanView.as_view(), name="scan"),
    path('mark/', views.MarkView.as_view(), name="mark"),
    path('login/', views.LoginView.as_view(), name="login"),
]