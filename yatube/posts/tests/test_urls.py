from http import HTTPStatus

from django.test import TestCase, Client

from posts.models import User, Group, Post


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.author = User.objects.create(username='author')
        group = Group.objects.create(
            title='Основная',
            slug='main',
            description='Для общих постов',
        )
        Post.objects.create(
            text='Длинный текст поста',
            author=cls.author,
            group=group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(PostUrlTests.author)
        self.user_client = Client()
        self.user_client.force_login(PostUrlTests.user)

    def test_accessible_urls_for_guest(self):
        """Основные просмотра доступны любому пользователю."""
        accessible_urls = [
            '/',
            '/group/main/',
            '/profile/author/',
            '/posts/1/',
        ]
        for url in accessible_urls:
            with self.subTest(value=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_inaccessible_urls_for_guest(self):
        """Страницы редактирования и создания постов
        перенаправляют неавторизованного пользователя.
        """
        inaccessible_urls = [
            '/posts/1/edit/',
            '/create/',
        ]
        for url in inaccessible_urls:
            with self.subTest(value=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response, '/auth/login/?next=' + url)

    def test_accessible_urls_for_author(self):
        """Страницы редактирования и создания постов
        доступны авторизованному пользователю.
        """
        accessible_urls = [
            '/posts/1/edit/',
            '/create/',
        ]
        for url in accessible_urls:
            with self.subTest(value=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_inaccessible_urls_for_user(self):
        """Страница редактирования поста перенаправляют не автора поста."""
        response = self.user_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/posts/1/')

    def test_unexisting_page(self):
        """Несуществующая страница выдает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_templates(self):
        """URL-адреса имеют соответствующий шаблон."""
        urls_template_names = {
            '/': 'posts/index.html',
            '/group/main/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in urls_template_names.items():
            with self.subTest(value=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
