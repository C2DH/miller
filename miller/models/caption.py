#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,codecs
import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from miller.models import Document, Story

class Caption(models.Model):
  document      = models.ForeignKey(Document, on_delete=models.CASCADE)
  story         = models.ForeignKey(Story, on_delete=models.CASCADE)
  date_created  = models.DateField(auto_now=True)

  contents      = models.TextField(blank=True, default='')

  class Meta:
    ordering = ["-date_created"]
    verbose_name_plural = "captions"

  def __unicode__(self):
    return '%s (%s)' % (self.story.slug, self.document.slug)


def collect_ids(obj):
    out = []
    if type(obj) == dict:
        for x in obj.keys():
            if x == 'id':
                out.append(obj[x])
            out.extend(collect_ids(obj[x]))

    if type(obj) == list:
        for x in obj:
            out.extend(collect_ids(x))

    return out


@receiver(post_save, sender=Story)
def chapter_links(sender, instance, created, **kwargs):
    """
    updates mentions between current chapter and documents used in modules
    """

    if not instance.tags.filter(pk=2).exists():
        return
    captions = instance.caption_set.all().delete()
    try:
        json_contents = json.loads(instance.contents)
    except:
        return

    doc_ids = collect_ids(json_contents)

    for pk in doc_ids:
        try:
            doc = Document.objects.get(pk=pk)
            Caption.objects.create(document=doc, story=instance)
        except Document.DoesNotExist:
            pass
