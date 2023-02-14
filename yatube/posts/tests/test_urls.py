from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Group, Post, User


GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тест описание'
USER_USERNAME = 'Anonimus'
USER_USERNAME1 = 'Vasya'
POST_TEXT = 'Тестовая запись для тестового поста номер'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.author = Client()
        cls.user_author = User.objects.create_user(username=USER_USERNAME1)
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.authorized_client.force_login(cls.user)
        cls.author.force_login(cls.user_author)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user_author,
            pk=1
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls = {
            '/': 'posts/index.html',
            '/profile/Anonimus/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/group/test-slug/': 'posts/group_list.html'
        }
        for address, template in templates_urls.items():
            with self.subTest(address=address):
                response = self.author.get(address)
                self.assertTemplateUsed(response, template)

    def test_correct_redirect(self):
        tests_datas = [
            ('/', self.guest_client, HTTPStatus.OK),
            ('/', self.authorized_client, HTTPStatus.OK),
            ('/profile/Anonimus/', self.guest_client, HTTPStatus.OK),
            ('/profile/Anonimus/', self.authorized_client, HTTPStatus.OK),
            ('/posts/1/', self.guest_client, HTTPStatus.OK),
            ('/posts/1/', self.authorized_client, HTTPStatus.OK),
            ('/create/', self.guest_client, HTTPStatus.FOUND),
            ('/create/', self.authorized_client, HTTPStatus.OK),
            ('/posts/1/edit/', self.guest_client, HTTPStatus.FOUND),
            ('/posts/1/edit/', self.authorized_client, HTTPStatus.FOUND),
            ('/posts/1/edit/', self.author, HTTPStatus.OK),
            ('/group/test-slug/', self.guest_client, HTTPStatus.OK),
            ('/group/test-slug/', self.authorized_client, HTTPStatus.OK),
            ('/posts/unexisting_page/',
             self.guest_client,
             HTTPStatus.NOT_FOUND),
            ('/posts/unexisting_page/',
             self.authorized_client,
             HTTPStatus.NOT_FOUND)

        ]

        for address, client, response_status in tests_datas:
            with self.subTest(address=address,
                              client=client,
                              response_status=response_status):
                response = client.get(address)
                self.assertEqual(response.status_code, response_status)
