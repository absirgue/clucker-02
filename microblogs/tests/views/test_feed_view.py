"""Tests of the feed view."""
from django.test import TestCase
from django.urls import reverse
from microblogs.forms import PostForm
from microblogs.tests.helpers import reverse_with_next
from microblogs.models import User


class FeedViewTestCase(TestCase):
    """Tests of the feed view."""

    fixtures = ['microblogs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('feed')
        self.user = User.objects.get(username='@johndoe')

    def test_feed_url(self):
        self.assertEqual(self.url, '/feed/')

    def test_get_feed(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PostForm))
        self.assertFalse(form.is_bound)

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
