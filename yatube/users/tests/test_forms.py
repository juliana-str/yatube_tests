from django.test import TestCase

from ..forms import CreationForm, User


class CreationFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.fields = CreationForm.objects.create(
            first_name='first_name',
            last_name='last_name',
            username='username',
            email='test@test.ru'
        )
