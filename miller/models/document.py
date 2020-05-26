import os
import logging
import dpath.util

from django.conf import settings
from django.db import models
from django.db import connection
from django.contrib.postgres.search import SearchVectorField
from django.contrib.auth.models import User
from ..fields import UTF8JSONField
from ..snapshots import create_snapshot
from ..utils.models import get_search_vector_query

logger = logging.getLogger(__name__)


def attachment_file_name(instance, filename):
    return os.path.join(instance.type, filename)


def private_attachment_file_name(instance, filename):
    return os.path.join(settings.MEDIA_PRIVATE_ROOT, instance.type, filename)


def snapshot_attachment_file_name(instance, filename):
    return os.path.join(instance.type, 'snapshots', filename)


class Document(models.Model):
    BIBLIOGRAPHIC_REFERENCE = 'bibtex'
    CROSSREF_REFERENCE = 'crossref'
    VIDEO_COVER = 'video-cover'
    PICTURE = 'picture'
    IMAGE = 'image'
    PHOTO = 'photo'
    VIDEO = 'video'
    AUDIO = 'audio'
    TEXT = 'text'
    PDF = 'pdf'
    RICH = 'rich'
    LINK = 'link'
    AV = 'audiovisual'

    ENTITY = 'entity'

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

    type       = models.CharField(max_length=24, choices=TYPE_CHOICES)
    short_url  = models.CharField(max_length=22, db_index=True, unique=True, blank=True)

    title      = models.CharField(max_length=500)
    slug       = models.CharField(max_length=150, unique=True, blank=True, db_index=True)

    # contents   = models.TextField(null=True, blank=True, default=json.dumps(DEFAULT_OEMBED, indent=1)) # OEMBED (JSON) metadata field, in different languages if available.

    data       = UTF8JSONField(verbose_name=u'data contents', help_text='JSON format', default=dict, blank=True)

    copyrights = models.TextField(null=True, blank=True,  default='')

    url        = models.URLField(max_length=500, null=True, blank=True)
    owner      = models.ForeignKey(User, on_delete=models.CASCADE); # at least the first author, the one who owns the file.
    attachment = models.FileField(upload_to=attachment_file_name, null=True, blank=True, max_length=200)
    snapshot   = models.FileField(upload_to=snapshot_attachment_file_name, null=True, blank=True, max_length=200)
    mimetype   = models.CharField(max_length=127, blank=True, default='')

    locked     = models.BooleanField(default=False) # prevent accidental override when it is not needed.

    # add search field
    search_vector = SearchVectorField(null=True, blank=True)

    # add last modified date
    # undirected
    documents  = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.slug

    def create_snapshot_from_attachment(self, override=True):
        """
        if there is an attachment, generate a PNG snapshot or similar.
        If snapshot is already present, look for override param
        """
        logger.debug('document pk:{} create_snapshot_from_attachment using type:{} ...'.format(
            self.pk,
            self.type,
        ))

        if not self.attachment or not getattr(self.attachment, 'path', None):
            logger.error('document pk:{} no attachment found! Skip.'.format(self.pk))
            return

        if not os.path.exists(self.attachment.path):
            logger.error('document pk:{} snapshot cannot be generated, attached file {} does not exist.'.format(
                self.pk,
                self.attachment.path,
            ))
            return
        # get snaphot path and its width / height
        snapshot,w,h = create_snapshot(basepath=self.type, source=self.attachment.path)
        # save document
        self.snapshot = snapshot
        self.data.update({
            'snapshot': {
                'width': w,
                'height': h
            }
        })
        self.save()

    def update_search_vector(self):
        """
        Fill the search_vector using self.data:
        e.g. get data['title'] if is a str or data['title']['en_US']
        according to the values contained into settings.LANGUAGES
        Note that is possible to configure stemmer using language configuration
        in this case consider to add a fourth value for each
        language tuple in settings.LANGUAGES
        (e.g. 'english')
        """
        q, contents = get_search_vector_query(
            instance=self,
            languages=settings.MILLER_LANGUAGES,
            simple_fields=settings.MILLER_VECTORS_SIMPLE_FIELDS,
            multilanguage_fields=settings.MILLER_VECTORS_MULTILANGUAGE_FIELDS,
        )
        if not contents:
            logger.error(
                f'update_search_vector failed for document:{self.pk} (empty?)'
            )
            return

        with connection.cursor() as cursor:
            to_be_executed = ''.join([
                """
                UPDATE miller_document
                SET search_vector = x.weighted_tsv FROM (
                    SELECT id,
                """,
                q,
                """
                    AS weighted_tsv
                        FROM miller_document
                        WHERE miller_document.id=%s
                ) AS x
                WHERE x.id = miller_document.id
                """
            ])
            cursor.execute(to_be_executed, [
                value
                for value, w, c in contents
            ] + [self.pk])
