from django.conf import settings
from django.db import models


class Document(models.Model):
  BIBLIOGRAPHIC_REFERENCE = 'bibtex'
  CROSSREF_REFERENCE = 'crossref'
  VIDEO_COVER = 'video-cover'
  PICTURE = 'picture'
  IMAGE   = 'image'
  PHOTO   = 'photo'
  VIDEO   = 'video'
  AUDIO   = 'audio'
  TEXT    = 'text'
  PDF     = 'pdf'
  RICH    = 'rich'
  LINK    = 'link'
  AV      = 'audiovisual'

  ENTITY      = 'entity'

  TYPE_CHOICES = (
    (BIBLIOGRAPHIC_REFERENCE, 'bibtex'),
    (CROSSREF_REFERENCE, 'bibtex'),
    (VIDEO_COVER, 'video interview'),
    (VIDEO, 'video'),
    (TEXT, 'text'),
    (PICTURE, 'picture'),
    (PDF, 'pdf'),
    (IMAGE, 'image'),
    (PHOTO, 'photo'),
    (RICH, 'rich'),
    (LINK, 'link'),
    (AV, 'audiovisual'),

    (ENTITY, 'entity: see data type property'), # use the type field inside data JsonField.
  ) + settings.MILLER_DOCUMENT_TYPE_CHOICES
