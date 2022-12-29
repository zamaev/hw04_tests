from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Group, Post


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='user')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Основная',
            slug='main',
            description='Для общих постов',
        )
        cls.post = Post.objects.create(
            text='Длинный текст поста',
            author=cls.author,
            group=cls.group,
        )
        cls.accessible_urls = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', args=(cls.group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args=(cls.author.username,)
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args=(cls.post.pk,)
            ): 'posts/post_detail.html',
        }
        cls.inaccessible_urls = {
            reverse(
                'posts:post_edit', args=(cls.post.pk,)
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
        }

    def setUp(self):
        self.author = PostUrlTests.author
        self.author_client = PostUrlTests.author_client
        self.user = PostUrlTests.user
        self.user_client = PostUrlTests.user_client
        self.group = PostUrlTests.group
        self.post = PostUrlTests.post
        self.accessible_urls = PostUrlTests.accessible_urls
        self.inaccessible_urls = PostUrlTests.inaccessible_urls

    def test_accessible_urls_for_guest(self):
        """Основные страницы просмотра доступны любому пользователю."""
        for url in self.accessible_urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_inaccessible_urls_for_guest(self):
        """Страницы редактирования и создания постов
        перенаправляют неавторизованного пользователя.
        """
        for url in self.inaccessible_urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    reverse('users:login') + '?next=' + url
                )

    def test_accessible_urls_for_author(self):
        """Страницы редактирования и создания постов
        доступны авторизованному пользователю.
        """
        for url in self.accessible_urls:
            with self.subTest(value=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_inaccessible_urls_for_user(self):
        """Страница редактирования поста перенаправляют не автора поста."""
        response = self.user_client.get(
            reverse('posts:post_edit', args=(self.post.pk,)))
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.pk,))
        )

    def test_unexisting_page(self):
        """Несуществующая страница выдает ошибку 404."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_templates(self):
        """URL-адреса имеют соответствующий шаблон."""
        for url, template in {**self.accessible_urls,
                              **self.inaccessible_urls}.items():
            with self.subTest(value=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
