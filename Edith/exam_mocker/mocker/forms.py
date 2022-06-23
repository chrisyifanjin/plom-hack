from django.contrib.auth.models import User
from django import forms
from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError
import fitz
from fitz import FileDataError


class SignupForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username: ")
    email = forms.EmailField(max_length=100, label="Email: ")
    password = forms.CharField(widget=forms.PasswordInput, label="Password: ")
    confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password: ")

    def clean(self):
        data = self.cleaned_data

        print(data)

        username = data['username']
        password = data['password']
        confirm = data['confirm']

        if 'email' not in data.keys():
            raise ValidationError("Invalid email.")

        if password != confirm:
            raise ValidationError("Passwords do not match.")

        users_with_same_username = User.objects.filter(username=username)
        if users_with_same_username:
            raise ValidationError("An account with that username already exists.")

        users_with_same_email = User.objects.filter(email=data['email'])
        if users_with_same_email:
            raise ValidationError("An account with that email address already exists.")


        return data


class PDFUploadForm(forms.Form):
    pdf = forms.FileField(
        allow_empty_file=False, 
        max_length=100, 
        label='', 
        widget=forms.FileInput(attrs={'accept':'application/pdf'}))

    def clean(self):
        data = self.cleaned_data
        pdf = data['pdf']

        if pdf.size > 1e+7: # bytes
            raise ValidationError("File size must be less than 10MB.")

        # Is there a way to validate as a PDF without reading it?
        try:
            pdf_doc = fitz.open(stream=pdf.read())
            if 'PDF' not in pdf_doc.metadata['format']:
                raise ValidationError("File is not a valid PDF.")

            # for page in pdf_doc:
            #     if page.bound().width != 612.0 and page.bound().height != 792:
            #         raise ValidationError("Not all pages are A4 size in portrait orientation.")
            
        except FileDataError or KeyError:
            raise ValidationError("File is not a valid PDF.")

        return data


class GuestPDFUploadForm(PDFUploadForm):
    captcha = CaptchaField()
        