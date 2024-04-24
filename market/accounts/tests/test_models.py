from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase


class UserModelTest(TestCase):
    """Класс для тестирования модели пользователя"""

    fixtures = ["01-groups.json", "02-users.json"]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

    def test_loaded_user_and_groups(self) -> None:
        self.assertEqual(get_user_model().objects.count(), 11)
        self.assertEqual(Group.objects.count(), 2)
