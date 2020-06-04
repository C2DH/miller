from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


class Tag(models.Model):
    KEYWORD = 'keyword'  # i.e, no special category at all
    BLOG = 'blog'  # items tagged as events are "news"
    HIGHLIGHTS = 'highlights'
    WRITING = 'writing'
    COLLECTION = 'collection'
    # things related to publishing activity,
    # I.E issue number that can be filtered by
    PUBLISHING = 'publishing'

    CATEGORY_CHOICES = (
        (KEYWORD, 'keyword'),
        (BLOG, 'blog'),
        (HIGHLIGHTS, 'highlights'),
        (WRITING, 'writing'),
        (COLLECTION, 'collection'),
        (PUBLISHING, 'publishing')
    ) + settings.MILLER_TAG_CATEGORY_CHOICES

    HIDDEN = 'hidden'
    # everyone can access that.
    PUBLIC = 'public'

    STATUS_CHOICES = (
        (HIDDEN, 'keep this hidden'),
        (PUBLIC, 'published tag'),
    )
    # e.g. 'Mr. E. Smith'
    name = models.CharField(max_length=100)
    # e.g. 'mr-e-smith'
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    # e.g. 'actor' or 'institution'
    category = models.CharField(
        max_length=32, choices=CATEGORY_CHOICES, default=KEYWORD)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PUBLIC)

    data = JSONField(default=dict)

    class Meta:
        unique_together = ('name', 'category')

    def __unicode__(self):
        return f'{self.name}({self.category})'
