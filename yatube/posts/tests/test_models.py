from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Post, Group, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='Обозначение группы',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост',
            group=cls.group
        )
        cls.comment = Comment.objects.create(post=cls.post,
                                             author=cls.user,
                                             text='Комментарий')

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        self.assertEqual(str(group), group.title)
        self.assertEqual(str(post), post.text[:15])

    def test_verbose_name_post(self):
        """verbose_name в полях Post совпадает
        с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор'

        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text_post(self):
        """ help_text в полях Post совпадает
        с ожиданием """
        post = PostModelTest.post
        field_help_text = {
            'text': 'Текст поста',
            'pub_date': '',
            'group': 'Группа',
            'author': 'Автор'
        }

        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_verbose_name_group(self):
        """verbose_name в полях Group совпадает
        с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Обозначение группы',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_help_text_group(self):
        """ help_text в полях Group совпадает
        с ожиданием """
        group = PostModelTest.group
        field_help_text = {
            'title': 'Назовите группу',
            'slug': 'Присвойте группе ярлык',
            'description': 'Дайте группе краткое описание',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_verbose_name_comments(self):
        """verbose_name в полях Comment совпадает
        с ожидаемым."""
        comment = PostModelTest.comment
        field_verboses = {
            'post': 'Комментарии к посту',
            'author': 'Автор комментария',
            'text': 'text',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected
                )

    def test_help_text_group_comments(self):
        """ help_text в полях Comment совпадает
        с ожиданием """
        comment = PostModelTest.comment
        field_help_text = {
            'post': 'Комментарии к посту',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected
                )
