#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, json

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from miller import helpers
from miller.models import Profile

logger = logging.getLogger('miller')


class Author(models.Model):
  fullname    = models.TextField()
  affiliation = models.TextField(null=True, blank=True) # e.g Government and Politics, University of Luxembpourg
  metadata    = models.TextField(null=True, blank=True, default=json.dumps({
    'firstname': '',
    'lastname': ''
  }, indent=1))
  slug        = models.CharField(max_length=140, unique=True, blank=True)
  user        = models.ForeignKey(User, related_name='authorship', blank=True, null=True, on_delete=models.CASCADE)

  class Meta:
    app_label="miller"

  def __unicode__(self):
    return u' '.join(filter(None,[
      self.fullname, 
      '(%s)'%self.user.username if self.user else None,
      self.affiliation
    ]))

  def save(self, *args, **kwargs):
    if not self.pk and not self.slug:
      self.slug = helpers.get_unique_slug(self, self.fullname)
    super(Author, self).save(*args, **kwargs)


# create an author whenever a Profile is created.
@receiver(post_save, sender=Profile)
def create_author(sender, instance, created, **kwargs):
  if created:
    fullname = u'%s %s' % (instance.user.first_name, instance.user.last_name) if instance.user.first_name else instance.user.username
    aut = Author(user=instance.user, fullname=fullname, metadata=json.dumps({
      'firstname': instance.user.first_name,
      'lastname': instance.user.last_name
    }, indent=1))
    aut.save()
    logger.debug('(user {pk:%s}) @post_save: author created.' % instance.pk)
