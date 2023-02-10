from http import HTTPStatus

from django import forms
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тест описание'
USER_USERNAME = 'Anonimus'
POST_TEXT = 'Тестовая запись для тестового поста номер'
FIRST_PAGE_COUNT = 10
SECOND_PAGE_COUNT = 3


class PaginatorViewsTest(TestCase):
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
        cls.posts_list = [
            Post.objects.create(
                text=POST_TEXT,
                author=cls.user,
                group=cls.group
            )
            for _ in range(
                FIRST_PAGE_COUNT
                + SECOND_PAGE_COUNT)
        ]

    def test_paginator(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': self.user})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 FIRST_PAGE_COUNT)

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse('posts:index') + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 SECOND_PAGE_COUNT)

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response.status_code, HTTPStatus.OK)
                page_obj = response.context.get('page_obj')
                self.assertIsNotNone(page_obj)
                self.assertIsInstance(page_obj, Page)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group_list = [
            Group.objects.create(
                title=f'{GROUP_TITLE} {i}',
                slug=f'{GROUP_SLUG}_{i}',
                description=GROUP_DESCRIPTION,
            )
            for i in range(SECOND_PAGE_COUNT)

        ]
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
        )
        cls.test_post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group_list[1]
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        temlate_for_edit = 'posts/create_post.html'
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': self.user})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
            temlate_for_edit: (
                reverse('posts:post_edit', kwargs={'post_id': self.post.id})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_in_context_correct(self):
        templates = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': self.user})
            ),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
        }
        for template, reverse_name in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                page_obj = response.context.get('page_obj')
                self.assertIsNotNone(page_obj)
                self.assertIsInstance(page_obj, Page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_main_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        expected = Post.objects.all()[0]
        self.assertEqual(response.context['page_obj'][0], expected)

    def test_group_post_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context.get('group'), self.group)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(reverse(
                'posts:profile',
                kwargs={'username': self.user})
            )
        )
        self.assertEqual(response.context.get('author'), self.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.id})
        ))
        self.assertEqual(response.context.get('post'), self.post)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.id})
        ))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertEqual(response.context.get('post'), self.post)
        self.assertEqual(response.context.get('is_edit'), True)

    def test_post_create_correct_redirect(self):
        response = self.client.get(
            reverse('posts:post_create'), follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect_url = (
            reverse('users:login') + '?next=' + reverse('posts:post_create')
        )
        self.assertRedirects(response, redirect_url)

    def test_post_edit_correct_redirect(self):
        response = self.client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect_url = (
            reverse('users:login') + '?next=' + reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertRedirects(response, redirect_url)

    def test_group_in_posts(self):
        urls = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user}),
            reverse('posts:group_list',
                    kwargs={'slug': self.group_list[1].slug}
                    ),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn(self.test_post, response.context['page_obj'])

    def test_post_not_in_other_groups(self):
        urls = (
                reverse('posts:group_list',
                        kwargs={'slug': self.group_list[0].slug}),
                reverse('posts:group_list',
                        kwargs={'slug': self.group_list[2].slug}),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertNotIn(self.test_post, response.context['page_obj'])
