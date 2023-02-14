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
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
            pk=1
        )
        cls.form = PostCreateFormTests()

    def test_create_post(self):
        """Валидная форма создает пост."""
        self.post_count = Post.objects.count()
        form_data = {
                'group': self.group.pk,
                'text': self.post.text,
        }
        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), self.post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.post.group,
                text=self.post.text,
                ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирования поста"""
        self.post_count = Post.objects.count()
        self.text_edit = self.post.text + 'correct'
        form_edit_data = {
                'group': self.group.pk,
                'text': self.text_edit,
        }
        response = self.authorised_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_edit_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}))
        self.assertEqual(Post.objects.count(), self.post_count)
        self.assertNotEqual(self.text_edit, self.post.text)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=self.text_edit,
            ).exists()
        )