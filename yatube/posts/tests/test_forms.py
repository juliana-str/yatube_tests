import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from ..models import Post


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            text='Тестовый текст',
            group='test-group'
        )
        cls.form = PostCreateFormTests()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """Валидная форма создает post."""
        self.post_count = Post.objects.count()
        form_data = {
                'group': self.group,
                'text': self.text,
        }
        response = self.guest_client.post(
            reverse('posts:index'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_create'))
        self.assertEqual(Post.objects.count(), self.post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group='test-group',
                text='Тестовый текст',
                ).exists()
        )
