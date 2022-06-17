from django.contrib.auth import get_user_model
from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache


from ..models import Group, Post, Follow


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='posts_test')
        cls.user2 = User.objects.create(username='follower')
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
            text='text',
            group=cls.group
        )
        cls.group_post = Post.objects.create(
            author=cls.user,
            text='text',
            group=cls.group,
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_paginator(self):
        """Паджинатор работает."""
        cache.clear()
        post_list = []
        for i in range(1, 12):
            post_list.append(Post(
                text='text' + str(i),
                author=self.user,
                group=self.group,
            ))
        Post.objects.bulk_create(post_list)

        templates_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', args={self.user}),
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_detail_page_show_correct_context(self):
        """Проверяем что post_detail имеет правильный context."""
        postdetail = reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(postdetail)
        test_post = response.context['post']
        self.check_post_detail(test_post)
        form_fields = {
            'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                comment_form = response.context.get('form').fields.get(value)
                self.assertIsInstance(comment_form, expected)

    def check_post_detail(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author.username, self.user.username)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_post_create_page_show_correct_context(self):
        """Проверяем что post_create имеет правильный context."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        is_edit = True
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertNotEqual(response.context["is_edit"], is_edit)

    def test_post_edit_page_show_correct_context(self):
        """Проверяем что post_edit имеет правильный context."""
        post = PostPagesTests.post
        url = reverse('posts:post_edit', kwargs={'post_id': f'{post.id}'})
        response = self.authorized_client.get(url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        is_edit = True
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context["is_edit"], is_edit)

    def test_main_pages_show_correct_context(self):
        """Тестовые страницы используют правильный
        контекст общедоступных страниц index / group_list / profile.
        """
        cache.clear()
        context = {reverse('posts:index'): self.post,
                   reverse('posts:group_list',
                           kwargs={'slug': self.group.slug,
                                   }): self.post,
                   reverse('posts:profile',
                           kwargs={'username': self.user.username,
                                   }): self.post,
                   }
        for reverse_page, object in context.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.guest_client.get(reverse_page)
                self.check_post_detail(
                    response.context['page_obj'][0])

    def test_grouped_post_show_in_pages(self):
        """Проверяем, что пост с группой попадает на страницы."""
        group_post_pages = {
            reverse('posts:index') + '?page=2': 2,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2': 2,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}) + '?page=2': 2,
        }
        for value, expected in group_post_pages.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(len(response.context["page_obj"]), expected)

    def test_new_group_page_dont_have_a_post(self):
        """Проверяем что на странице другой группы нет постов."""
        url = reverse('posts:group_list', args=['posts_test_slug2'])
        response = self.authorized_client.get(url)
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_cache_on_index_page_works_correct(self):
        """Кэширование данных на главной странице работает корректно."""
        response = self.client.get(reverse('posts:index'))
        cached_content = response.content
        Post.objects.all().delete()
        response = self.client.get(reverse('posts:index'))
        cached_content_after_delete = response.content
        self.assertEqual(
            cached_content,
            cached_content_after_delete,
            'Кэширование работает некорректно.'
        )
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(
            cached_content,
            response.content,
            'Кэширование после очистки работает некорректно'
        )

    def test_follow(self):
        follow_count = Follow.objects.count()
        self.authorized_client2.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user}), follow=True)
        self.assertEqual(follow_count + 1, Follow.objects.count())
        self.assertTrue(Follow.objects.filter(
            user=self.user2, author=self.user))

    def test_unfollow(self):
        Follow.objects.create(author=self.user, user=self.user2)
        follow_count = Follow.objects.count()
        self.authorized_client2.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.user.username}))
        self.assertEqual(follow_count - 1, Follow.objects.count())

    def test_author_posts_for_follow_feed(self):
        """Записи появляются в ленте подписчиков
        и не появляется у тех, кто не подписан"""
        Follow.objects.create(
            user=self.user, author=PostPagesTests.user
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_post_on_follow = response.context['page_obj'][0]
        self.assertEqual(first_post_on_follow.author, PostPagesTests.user)
        not_follower = User.objects.create_user(username='NoFollow')
        not_follower_client = Client()
        not_follower_client.force_login(not_follower)
        response = not_follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
