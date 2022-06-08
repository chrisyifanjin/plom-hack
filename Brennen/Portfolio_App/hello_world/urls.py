from django.urls import path
from hello_world import views

# here is to create a list of URL patterns that correspond to the various view functions
urlpatterns = [
    path('', views.hello_world, name='hello_world'),
]
