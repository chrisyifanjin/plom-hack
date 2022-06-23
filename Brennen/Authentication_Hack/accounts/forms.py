from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

"""
This is the collection of forms to be use in a website. 
Also can customize the default form that django gives us.
"""


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
