from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/all/', views.CreateTasks.as_view(), name='create_tasks'),
    path('start/<str:task_id>', views.StartTask.as_view(), name='start_task'),
    path('start/all/', views.StartAll.as_view(), name='start_all'),
    path('cancel/<str:task_id>', views.CancelTask.as_view(), name='cancel_task'),
    path('retry/<str:task_id>', views.RetryTask.as_view(), name='retry_task'),
    path('retry/all/', views.RetryAll.as_view(), name='retry_all'),
    path('get_pdf/<str:task_id>', views.GetPDF.as_view(), name="get_pdf"),
    path('clear/everything/', views.ClearEverything.as_view(), name="clear_everything"),
    path('refresh/', views.Refresh.as_view(), name='refresh'),
]