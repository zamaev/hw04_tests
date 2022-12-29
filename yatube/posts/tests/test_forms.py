from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Group, Post


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='group',
            description='Группа для постов',
        )
        cls.new_group = Group.objects.create(
            title='Новая группа',
            slug='new_group',
            description='Новая группа для постов',
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        with self.subTest(value='posts_count'):
            self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        post = Post.objects.first()
        fileds_for_check = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.author: self.user,
        }
        for field, expected in fileds_for_check.items():
            with self.subTest(velue=post):
                self.assertEqual(field, expected)

    def test_guest_cannot_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        with self.subTest(value='posts_count'):
            self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create',)
        )

    def test_edit_post(self):
        """Валидная форма создает изменяет в Post."""
        form_data = {
            'text': 'Новый текст поста',
            'group': self.new_group.pk,
        }
        self.auth_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(pk=self.post.pk)
        fileds_for_check = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.author: self.post.author,
        }
        for field, expected in fileds_for_check.items():
            with self.subTest(velue=post):
                self.assertEqual(field, expected)

    def test_guest_cannot_edit_post(self):
        """Неавторизованный пользователь не может редактировать пост."""
        form_data = {
            'text': 'Новый текст поста',
            'group': self.new_group.pk,
        }
        response = self.client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_edit',
                                                        args=(self.post.pk,))
        )
