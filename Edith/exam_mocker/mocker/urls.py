from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('accounts/signup', views.SignupView.as_view(), name='signup'),
    path('upload/', views.LoginUploadView.as_view(), name='upload'),
    path('<int:pk>/mock', views.pdf_convert, name='mock'),
    path('linkgen/', views.GenerateLinkView.as_view(), name='generate'),
    re_path(r'upload/guest(?P<token>[\w_-]*$)', views.GuestUploadView.as_view(), name='guest_upload')
]

# Django auth views
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]

# captcha
urlpatterns += [
    path('captcha/', include('captcha.urls')),
]
