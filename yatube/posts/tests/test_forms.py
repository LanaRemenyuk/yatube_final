from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..forms import PostForm
from http import HTTPStatus
import shutil
import tempfile

from ..models import Group, Post, Comment


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='posts_test_slug',
            description='test desc',
        )
        cls.group2 = Group.objects.create(
            title='test group 2',
            slug='posts_test_slug2',
            description='test desc 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост',
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormsTests.user)

    def test_count_create_existing_field(self):
        """
        Проверяем при отправке валидной формы со страницы редактирования
        поста reverse('posts:post_edit') создаётся новая запись в базе данных.
        """
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test text',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:profile', args={self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.latest('pub_date')
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.image, f"posts/{form_data['image']}")
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_valid_post(self):
        """
        Проверяем при отправке валидной формы со страницы редактирования
        поста reverse('posts:post_edit') меняется запись в базе данных.
        """
        posts_count = Post.objects.count()
        groupnew = PostFormsTests.group2.id
        form_data = {
            'text': 'Пост',
            'group': groupnew,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group.id)

    def test_add_comment_form(self):
        """Проверка добавления комментариев пользователями"""
        form_data = {
            'text': 'Текст комментария',
            'author': PostFormsTests.user,
            'post': self.post
        }
        Client().post(
            reverse('posts:add_comment', args={self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), 0)
        self.assertFalse(
            Comment.objects.filter(
                text='Текст комментария',
                author=PostFormsTests.user,
                post=self.post
            ).exists())
        self.authorized_client.post(
            reverse('posts:add_comment', args={self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Текст комментария',
                author=PostFormsTests.user,
                post=self.post
            ).exists())
