import logging
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..utils.models import create_short_url

logger = logging.getLogger(__name__)


class Profile(models.Model):
    NEWSLETTER_WEEKLY = 'W'
    NEWSLETTER_MONTHLY = 'M'
    NEWSLETTER_NEVER = '0'

    NEWSLETTER_CHOICES = (
        (NEWSLETTER_WEEKLY, 'weekly'),
        (NEWSLETTER_MONTHLY, 'monthly'),
        (NEWSLETTER_NEVER, 'never'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    short_url = models.CharField(
        max_length=22, default=create_short_url, unique=True
    )
    bio = models.TextField(null=True, blank=True)
    picture = models.URLField(max_length=160, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)
    date_last_notified = models.DateTimeField(auto_now_add=True)

    newsletter = models.CharField(
        max_length=1, choices=NEWSLETTER_CHOICES,
        default=NEWSLETTER_WEEKLY
    )

    def __str__(self):
        return self.user.username
# Create a folder to store user contents: stories, files etc..
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not instance.profile:
        pro = Profile(user=instance)
        pro.save()
        logger.debug(f'create_profile (user {instance.pk}) @post_save: done.')
