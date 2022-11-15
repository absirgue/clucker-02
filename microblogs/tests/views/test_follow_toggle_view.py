from django.test import TestCase
from django.urls import reverse
from microblogs.models import User
from microblogs.tests.helpers import reverse_with_next


class ShowUserTest(TestCase):
    fixtures = ['microblogs/tests/fixtures/default_user.json',
                'microblogs/tests/fixtures/other_users.json'
                ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('follow_toggle', kwargs={'user_id': self.user.id})

    def test_follow_toggle_url(self):
        self.assertEqual(self.url, f'/follow_toggle/{self.user.id}')
