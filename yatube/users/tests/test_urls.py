from http import HTTPStatus

from django.test import TestCase, Client

from posts.models import User


class UserUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(UserUrlTest.user)

    def test_accessible_urls_guest(self):
        """Страницы доступны любому пользователю."""
        accessible_urls = {
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/uidb64/token/',
            '/auth/reset/done/',
        }
        for url in accessible_urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_inuccessible_urls_guest(self):
        """Страницы не доступны не авторизованному пользователю."""
        inaccessible_urls = {
            '/auth/password_change/',
            '/auth/password_change/done/',
        }
        for url in inaccessible_urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_accessible_urls_user(self):
        """Страницы доступны авторизованному пользователю."""
        accessible_urls = {
            '/auth/password_change/',
            '/auth/password_change/done/',
        }
        for url in accessible_urls:
            with self.subTest(value=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_templates(self):
        """URL адреса используют соответствующий шаблон."""
        urls_template_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/uidb64/token/': 'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in urls_template_names.items():
            with self.subTest(template, value=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)
