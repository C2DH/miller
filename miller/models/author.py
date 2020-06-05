from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from ..fields import UTF8JSONField

orcid_regex = RegexValidator(
    regex=r'^[\d\-]+$',
    message="ORCID should contain only numbers and '-' sign")


class Author(models.Model):
    slug = models.CharField(max_length=140, unique=True, blank=True)

    fullname = models.TextField()
    affiliation = models.TextField(null=True, blank=True)

    data = UTF8JSONField(
        verbose_name=u'data contents', help_text='JSON format',
        default=dict, blank=True
    )

    orcid = models.CharField(
        max_length=24,
        validators=[orcid_regex], blank=True)
    user = models.ForeignKey(
        User, related_name='authorship', blank=True,
        null=True, on_delete=models.CASCADE)
