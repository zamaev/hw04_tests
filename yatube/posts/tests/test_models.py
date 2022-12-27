from django.test import TestCase

from posts.models import User, Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Группа',
            slug='gruppa',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Очень длинный текст больше 15 символов',
            author=cls.author,
            group=cls.group,
        )

    def test_model_have_correct_object_name(self):
        """В поле __str__ объекта post записано значение поля post.title."""
        post = PostModelTest.post
        expected_post_name = post.text[:15]
        self.assertEqual(expected_post_name, str(post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected in field_verboses.items():
            with self.subTest(value=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, exptected in field_help_texts.items():
            with self.subTest(value=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, exptected)
