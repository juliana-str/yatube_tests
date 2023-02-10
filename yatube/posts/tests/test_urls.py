from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User


GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тест описание'
USER_USERNAME = 'Anonimus'
POST_TEXT = 'Тестовая запись для тестового поста номер'


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
        )

    # Проверяем доступ для неавторизованного пользователя
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    # Проверяем доступ для авторизованного пользователя
    def test_urls_uses_correct_template_for_authorized_client(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls = {
            'posts/index.html': '/',
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, address in templates_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    # Проверяем доступ для авторизованного пользователя(автора поста)
    def test_post_edit_url_uses_correct_template(self):
        """Страница /posts/post_id/edit/ доступна авторизованному
        пользователю(автору поста)."""
        if self.authorized_client.force_login(self.user) == self.post.author:
            response = self.authorized_client.get(
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
            self.assertTemplateUsed(response, 'posts/create_post.html')
        else:
            response = self.authorized_client.get(
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
            self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редирект для авторизованного пользователя
    def test_post_detail_url_exists_at_desired_location_authorized(self):
        """Страница /posts/post_id/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_post_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /post_id/edit/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/posts/post_id/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_existing_page_url_redirect_anonymous(self):
        """Страница /unexisting_page/ перенаправляет пользователя."""
        response = self.guest_client.get('/posts/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
