from math import ceil

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import User, Group, Post


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.empty_group = Group.objects.create(
            title='Пустая',
            slug='empty',
            description='Без постов',
        )
        cls.main_group = Group.objects.create(
            title='Основная',
            slug='main',
            description='Для общих постов',
        )
        cls.post_without_group = Post.objects.create(
            text='Текст поста без группы',
            author=cls.user
        )
        cls.post_with_group = Post.objects.create(
            text='Текст поста с группой',
            group=cls.main_group,
            author=cls.user
        )

    def setUp(self):
        self.user = PostViewTests.user
        self.auth_client = PostViewTests.auth_client
        self.empty_group = PostViewTests.empty_group
        self.main_group = PostViewTests.main_group
        self.post_without_group = PostViewTests.post_without_group
        self.post_with_group = PostViewTests.post_with_group

    def test_pages_uses_correct_templates(self):
        """URL адреса используют соответствующий шаблон."""
        pages_template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                args=(self.main_group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=(self.user.username,)
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args=(self.post_without_group.pk,)
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                args=(self.post_without_group.pk,)
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
        необходимый пост.
        """
        urls = {
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.main_group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        }
        for url in urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertGreaterEqual(len(response.context['page_obj']), 1)
                self.check_posts_are_same(
                    response.context['page_obj'][0],
                    self.post_with_group
                )

    def test_empty_group_page_list_is_0(self):
        """На странице группы без добавления постов нет постов."""
        response = self.client.get(
            reverse('posts:group_list', args=(self.empty_group.slug,)))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон страницы профиля сформирован с правильным конекстом."""
        response = self.client.get(
            reverse('posts:profile', args=(self.user.username,)))
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон страницы поста сформирован с правильным контекстом."""
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post_without_group.pk,)))
        self.check_posts_are_same(
            response.context['post'],
            self.post_without_group,
        )

    def test_post_pages_with_form_show_correct_context(self):
        """Страницы с формами сформированы с правильным контекстом."""
        pages = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=(self.post_without_group.pk,)),
        ]
        for page in pages:
            response = self.auth_client.get(page)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField,
            }
            for field, expected in form_fields.items():
                with self.subTest(value=field):
                    self.assertIsInstance(
                        response.context['form'].fields[field],
                        expected
                    )

    def test_post_edit_form_show_correct_context_instance(self):
        """Страница редактирования поста сформирована с правильным контекстом
        с нужным постом для редактирования.
        """
        response = self.auth_client.get(
            reverse('posts:post_edit', args=(self.post_without_group.pk,)))
        instance = response.context['form'].instance
        self.assertEqual(instance.text, 'Текст поста без группы')
        self.assertEqual(instance.author, self.user)

    def check_posts_are_same(self, post1, post2):
        fields_for_check = [
            'text',
            'pub_date',
            'author',
            'group',
        ]
        for field in fields_for_check:
            with self.subTest(value=field):
                self.assertEqual(
                    getattr(post1, field),
                    getattr(post2, field)
                )


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='group',
            description='Для постов',
        )
        cls.posts_count_for_test = 13
        for i in range(cls.posts_count_for_test):
            Post.objects.create(
                text='Длинный текст поста ' + str(i),
                group=cls.group,
                author=cls.user,
            )

    def setUp(self):
        self.user = PaginatorViewTest.user
        self.group = PaginatorViewTest.group
        self.posts_count_for_test = PaginatorViewTest.posts_count_for_test

    def test_list_pages_check_records_count(self):
        """Кол-во постов в пагинации на каждой из страниц со списками."""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        ]
        for url in urls:
            with self.subTest(value=url):
                pages = ceil(
                    self.posts_count_for_test / settings.POSTS_PER_PAGE
                )
                for page in range(1, pages + 1):
                    response = self.client.get(url, {'page': page})
                    if page == pages:
                        posts_count_on_page = (self.posts_count_for_test
                                               % settings.POSTS_PER_PAGE)
                    else:
                        posts_count_on_page = settings.POSTS_PER_PAGE
                    self.assertEqual(
                        len(response.context['page_obj']),
                        posts_count_on_page,
                    )
