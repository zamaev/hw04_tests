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
        Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostFormTest.user)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': PostFormTest.group.pk,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'user'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма создает изменяет в Post."""
        post_id = 1
        form_data = {
            'text': 'Новый текст поста',
            'group': PostFormTest.group.pk,
        }
        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(pk=post_id)
        self.assertEqual(post.text, form_data['text'])
