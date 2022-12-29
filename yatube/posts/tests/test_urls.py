from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Group, Post


class PostUrlTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.author = User.objects.create(username='author')
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user = User.objects.create(username='user')
        self.user_client = Client()
        self.user_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Основная',
            slug='main',
            description='Для общих постов',
        )
        self.post = Post.objects.create(
            text='Длинный текст поста',
            author=self.author,
            group=self.group,
        )

    def test_accessible_urls_for_guest(self):
        """Основные страницы просмотра доступны любому пользователю."""
        accessible_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.author.username,)),
            reverse('posts:post_detail', args=(self.post.pk,)),
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
            reverse('posts:post_edit', args=(self.post.pk,)),
            reverse('posts:post_create'),
        ]
        for url in inaccessible_urls:
            with self.subTest(value=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response,
                    reverse('users:login') + '?next=' + url
                )

    def test_accessible_urls_for_author(self):
        """Страницы редактирования и создания постов
        доступны авторизованному пользователю.
        """
        accessible_urls = [
            reverse('posts:post_edit', args=(self.post.pk,)),
            reverse('posts:post_create'),
        ]
        for url in accessible_urls:
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
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_templates(self):
        """URL-адреса имеют соответствующий шаблон."""
        urls_template_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', args=(self.group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args=(self.author.username,)
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args=(self.post.pk,)
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', args=(self.post.pk,)
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
        }
        for url, template in urls_template_names.items():
            with self.subTest(value=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
