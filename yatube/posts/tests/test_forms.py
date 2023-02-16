from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тест описание'
USER_USERNAME = 'Anonimus'
POST_TEXT = 'Тестовая запись для тестового поста номер'


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.authorised_client = Client()
        cls.authorised_client.force_login(cls.user)
        cls.the_group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.the_post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.the_group,
        )

    def test_create_post(self):
        """Валидная форма создает пост."""
        post_count = Post.objects.count()
        form_data = {
            'group': self.the_group.pk,
            'text': 'simple test',
        }
        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        last_post = Post.objects.latest('pub_date')
        self.assertEqual(last_post.group, self.the_post.group)
        self.assertEqual(last_post.author, self.the_post.author)
        self.assertEqual(last_post.text, 'simple test')

    def test_post_edit(self):
        """Валидная форма редактирования поста"""
        another_group = Group.objects.create(
            title=GROUP_TITLE + ' 1',
            slug=GROUP_SLUG + '1',
            description=GROUP_DESCRIPTION
        )
        post_count = Post.objects.count()
        form_edit_data = {
            'group': another_group.pk,
            'text': self.the_post.text + ' 1',
        }
        response = self.authorised_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.the_post.pk}),
            data=form_edit_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.the_post.pk}))
        self.assertEqual(Post.objects.count(), post_count)
        edit_post = Post.objects.get(pk=self.the_post.pk)
        self.assertEqual(form_edit_data['text'], edit_post.text)
        self.assertEqual(another_group, edit_post.group)
        self.assertEqual(self.the_post.author, edit_post.author)
