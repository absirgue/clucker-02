"""Models in the microblogs app."""

from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar


class User(AbstractUser):
    """User model used for authentication and microblog authoring."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='followees')

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def is_following(self, user):
        return user in self.followees.all()

    def toggle_follow(self, user):
        if (self.is_following(user)):
            self.unfollow(user)
        else:
            self.follow(user)

    def follow(self, user):
        user.followers.add(self)

    def unfollow(self, user):
        user.followers.remove(self)

    def follower_count(self):
        return self.followers.count()

    def followee_count(self):
        return self.followees.count()


class Post(models.Model):
    """Posts by users in their microblogs."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model options."""

        ordering = ['-created_at']
