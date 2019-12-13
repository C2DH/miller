from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

class Tag(models.Model):
  # categories
  KEYWORD = 'keyword' # i.e, no special category at all
  BLOG   = 'blog' # items tagged as events are "news"
  HIGHLIGHTS   = 'highlights'
  WRITING      = 'writing'
  COLLECTION   = 'collection'
  PUBLISHING   = 'publishing' # things related to publishing activity, I.E issue number that can be filtered by

  CATEGORY_CHOICES = (
    (KEYWORD, 'keyword'),
    (BLOG, 'blog'),
    (HIGHLIGHTS, 'highlights'),
    (WRITING, 'writing'),
    (COLLECTION, 'collection'),
    (PUBLISHING, 'publishing')
  ) + settings.MILLER_TAG_CATEGORY_CHOICES

  HIDDEN  = 'hidden'
  PUBLIC  = 'public' # everyone can access that.

  STATUS_CHOICES = (
    (HIDDEN, 'keep this hidden'),
    (PUBLIC, 'published tag'),
  )

  name       = models.CharField(max_length=100) # e.g. 'Mr. E. Smith'
  slug       = models.SlugField(max_length=100, unique=True, blank=True) # e.g. 'mr-e-smith'
  category   = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default=KEYWORD) # e.g. 'actor' or 'institution'
  status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PUBLIC)

  data       = JSONField(default=dict)

  # search     = models.TextField(null=True, blank=True)# SearchVectorField(null=True, blank=True) # index search

  class Meta:
    unique_together = ('name', 'category')

  def __unicode__(self):
    return '%s (%s)' % (self.name, self.category)
