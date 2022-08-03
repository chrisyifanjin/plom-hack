from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home_view, name='index'),
    path("new_task/add", views.create_add_task_view, name='create_add_task'),
    path("new_task/gen", views.create_gen_task_view, name='create_guess_task'),
    path("new_task/gen/<str:uuid>", views.retry_gen_task_view, name='retry_guess_task'),
    path("task/<str:uuid>", views.task_view, name="view_task"),
    path("refresh/<str:uuid>", views.get_task_status_view, name="refresh"),
    path("get_tasks/", views.get_task_list, name="get_tasks"),
    path("clear_tasks/", views.delete_tasks_view, name='clear_tasks'),
    path("refresh_ml/", views.get_task_status_ml_view, name="refresh_ml"),
    path("train/", views.train_page_view, name="train"),
]

# authentication views
urlpatterns += [
    path('login/', auth_views.LoginView.as_view(next_page='index'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/log_out.html'), name='logout'),
]