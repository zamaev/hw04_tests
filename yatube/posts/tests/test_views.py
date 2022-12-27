from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import User, Group, Post


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        Group.objects.create(
            title='Пустая',
            slug='empty',
            description='Без постов',
        )
        cls.main_group = Group.objects.create(
            title='Основная',
            slug='main',
            description='Для общих постов',
        )
        Post.objects.create(
            text='Текст поста без группы',
            author=cls.user
        )
        Post.objects.create(
            text='Текст поста с группой',
            group=cls.main_group,
            author=cls.user
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostViewTests.user)

    def test_pages_uses_correct_templates(self):
        """URL адреса используют соответствующий шаблон."""
        pages_template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'main'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'user'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 1}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': 1}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create',
            ): 'posts/create_post.html',
        }
        for url, template in pages_template_names.items():
            with self.subTest(value=url):
                request = self.auth_client.get(url)
                self.assertTemplateUsed(request, template)

    def test_list_pages_show_correct_context(self):
        """На всех страницах со списком постов отображается
        необходимый поста.
        """
        pages = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'main'}),
            reverse('posts:profile', kwargs={'username': 'user'}),
        }
        for page in pages:
            with self.subTest(value=page):
                response = self.client.get(page)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, 'Текст поста с группой')
                self.assertEqual(first_object.group, PostViewTests.main_group)
                self.assertEqual(first_object.author, PostViewTests.user)

    def test_empty_group_page_list_is_0(self):
        """На странице группы без добавления постов нет постов."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'empty'}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон страницы профиля сформирован с правильным конекстом."""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'user'}))
        self.assertEqual(response.context['author'].username, 'user')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон страницы поста сформирован с правильным контекстом."""
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        self.assertEqual(
            response.context['post'].text,
            'Текст поста без группы',
        )

    def test_post_pages_with_form_show_correct_context(self):
        """Страницы с формами сформированы с правильным контекстом."""
        pages = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': 1}),
        ]
        for page in pages:
            response = self.auth_client.get(page)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField,
            }
            for field, expected in form_fields.items():
                with self.subTest(value=field):
                    value = response.context['form'].fields[field]
                    self.assertIsInstance(value, expected)

    def test_post_edit_form_show_correct_context_instance(self):
        """Страница редактирования поста сформирована с правильным контекстом
        с нужным постом для редактирования.
        """
        response = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
        instance = response.context['form'].instance
        self.assertEqual(instance.text, 'Текст поста без группы')
        self.assertEqual(instance.author, PostViewTests.user)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(username='user')
        group = Group.objects.create(
            title='Группа',
            slug='group',
            description='Для постов',
        )
        for i in range(1, 14):
            Post.objects.create(
                text='Длинный текст поста ' + str(i),
                group=group,
                author=user
            )

    def test_list_pages_check_records_count(self):
        """Кол-во постов в пагинации на каждой из страниц со списками."""
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'group'}),
            reverse('posts:profile', kwargs={'username': 'user'}),
        ]
        for page in pages:
            with self.subTest(value=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
