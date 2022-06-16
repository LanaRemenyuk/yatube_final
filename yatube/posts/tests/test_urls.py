from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(slug='group_slug')
        cls.user = User.objects.create(username='USERNAME')
        cls.author = User.objects.create_user(
            username='author_of_Posts')
        cls.post = Post.objects.create(
            author=User.objects.get(username='author_of_Posts'),
            text='Пост',
            group=cls.group,
        )

    def setUp(self) -> None:
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем клиент для проверки редиректа при изменении чужого поста
        self.authorized_client_not_author = Client(self.author)

    # Проверяем общедоступные страницы
    def test_pages_exists_at_desired_location_for_all(self):
        """Страница доступна любому пользователю"""
        pages_url = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }

        for address, http_status in pages_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, http_status)

    # Проверяем страницы, доступные только авторизованному пользователю
    def test_pages_exists_at_desired_location_for_authorized(self):
        """Страница доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем страницы, доступные только автору
    def test_pages_exists_at_desired_location_for_author(self):
        """Страница доступна автору"""
        response = self.authorized_client_not_author.\
            get(f'/posts/{self.post.id}/edit/')
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, ('/auth/login/?next=/posts/1/edit/'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_detail_url_redirect_anonymous(self):
        """Страница /posts/<post_id>/edit/ перенаправляет не автора поста."""
        response = self.authorized_client.\
            get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, reverse(
            'posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_page_redirects_comment_follow_unfollow(self):
        """Страницы перенаправляют авторизованных пользователей."""
        response = self.authorized_client. \
            get(f'/posts/{self.post.id}/comment/')
        self.assertRedirects(response, reverse(
            'posts:post_detail', args={self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        response = self.authorized_client. \
            get(f'/profile/{self.user}/follow/')
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.user}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        response = self.authorized_client. \
            get(f'/profile/{self.user}/unfollow/')
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.user}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_public_urls_uses_correct_template(self):
        """Общедоступный URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        url_names_for_templates = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            "/unexisting_page/": "posts/core/404.html"
        }

        for address, template in url_names_for_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_private_urls_uses_correct_template(self):
        """ URL-адрес для авторизованных пользователей
         использует соответствующий шаблон."""
        cache.clear()
        # Шаблоны по адресам
        url_names_for_templates = {
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for address, template in url_names_for_templates.items():
            with self.subTest(address=address):
                self.authorized_client.force_login(self.author)
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
