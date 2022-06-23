import os
import shutil
from time import sleep
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.core.cache import cache
from . import services
from . import views


def create_sample_pdf():
    return SimpleUploadedFile("Upload Pdf.pdf", b"Hello world!", content_type="pdf")

def create_test_user():
    return User.objects.create(username='edith', password='hunter2')

def create_and_login_test_user(client):
    user = User.objects.create(username='edith', password='hunter2')
    client.post(reverse('login'), {'username': user.username, 'password': user.password})
    return user


class TestPDFUpload(TestCase):
    def test_upload(self):
        sample_pdf = create_sample_pdf()
        uploaded_pdf = services.create_uploaded_pdf(0, False, sample_pdf)

        self.assertEquals(uploaded_pdf.filename_slug, 'upload-pdf')
        self.assertEquals(uploaded_pdf.user_id, 0)
        self.assertTrue(os.path.exists(f'media/user0/{uploaded_pdf.filename_slug}.pdf'))

        shutil.rmtree('media/user0/')

    def test_delete(self):
        sample_pdf = create_sample_pdf()
        uploaded_pdf = services.create_uploaded_pdf(0, True, sample_pdf)
        slug = uploaded_pdf.filename_slug
        services.delete_uploaded_pdf(uploaded_pdf)

        self.assertFalse(os.path.exists(f'media/guest0/{slug}.pdf'))
        self.assertFalse(os.path.exists(f'media/guest0'))
    

class TestAuthenticaion(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_login(self):
        test_user = create_test_user()

        cli = Client()
        response = cli.post(reverse('login'), {'username': test_user.username, 'password': test_user.password})
        self.assertEquals(response.status_code, 200)

    def test_access_upload_page(self):
        cli = Client()

        response = cli.get(reverse('upload'), follow=True)
        self.assertRedirects(response, reverse('login') + '?next=/upload/', 302)

        test_user = create_and_login_test_user(cli)
        response = cli.get(reverse('upload'), follow=True)
        self.assertEquals(response.status_code, 200)

    def test_access_linkgen_page(self):
        cli = Client()

        response = cli.get(reverse('generate'), follow=True)
        self.assertRedirects(response, reverse('login') + '?next=/linkgen/', 302)

        test_user = create_and_login_test_user(cli)
        response = cli.get(reverse('generate'), follow=True)
        self.assertEquals(response.status_code, 200)

    def test_generate_link(self):
        generate_view = views.GenerateLinkView()
        token = 'test_token'
        link = generate_view.generate_link(token, None, '')
        
        self.assertEquals(link, f'/upload/guest?token={token}')

    def test_guest_link_timeout(self):
        cli = Client()
        test_token = 'testtoken'

        request = cli.get(f'/upload/guest?token={test_token}')
        self.assertEquals(request.status_code, 403)

        # generate a new link, add to cache
        generate_view = views.GenerateLinkView()
        link = generate_view.generate_link(test_token, 1, '')

        # test that it's in the cache
        self.assertEquals(cache.get(test_token), 1)

        # use token, which should clear, wait 1 second, and it should fail
        request = cli.get(f'/upload/guest?token={test_token}')
        self.assertEquals(request.status_code, 200)

        sleep(1)

        request = cli.get(f'/upload/guest?token={test_token}')
        self.assertEquals(request.status_code, 403)
