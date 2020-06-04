import os
import logging
import shortuuid
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


def create_short_url():
    return shortuuid.uuid()[:7]  # => "IRVaY2b"


class Document(models.Model):
    TBD = 'to be defined'
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
        (TBD, 'to be defined'),
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
        # for ENTITY, use the type field inside data JsonField.
        (ENTITY, 'entity: see data type property'),
    ) + settings.MILLER_DOCUMENT_TYPE_CHOICES

    type = models.CharField(max_length=24, choices=TYPE_CHOICES, default=TBD)
    short_url = models.CharField(
        max_length=22, db_index=True, unique=True, blank=True,
        default=create_short_url
    )

    title = models.CharField(max_length=500, default='')
    slug = models.CharField(
        max_length=150, unique=True, blank=True, db_index=True
    )

    data = UTF8JSONField(
        verbose_name=u'data contents', help_text='JSON format',
        default=dict, blank=True
    )

    copyrights = models.TextField(null=True, blank=True,  default='')

    url = models.URLField(max_length=500, null=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        null=True, blank=True
    )
    attachment = models.FileField(
        upload_to=attachment_file_name,
        null=True, blank=True, max_length=200
    )
    snapshot = models.FileField(
        upload_to=snapshot_attachment_file_name,
        null=True, blank=True, max_length=200
    )
    mimetype = models.CharField(max_length=127, blank=True, default='')

    # @TODO prevent accidental override when it is not needed.
    locked = models.BooleanField(default=False)

    # add search field
    search_vector = SearchVectorField(null=True, blank=True)

    # add last modified date
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    # undirected links
    documents = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.slug

    def create_snapshot_from_attachment(self, override=True):
        """
        if there is an attachment, generate a PNG snapshot or similar.
        If snapshot is already present, look for override param
        """
        logger.debug(
            f'create_snapshot_from_attachment document pk:{self.pk}'
            f' using type:{self.type} ...'
        )

        if not self.attachment or not getattr(self.attachment, 'path', None):
            logger.error(
                f'create_snapshot_from_attachment document pk:{self.pk}'
                f' failed, no attachment found! Skip.')
            return

        if not os.path.exists(self.attachment.path):
            logger.error(
                f'create_snapshot_from_attachment document pk:{self.pk}'
                ' failed, attached file {self.attachment.path} does not exist.'
            )
            return
        # get snaphot path and its width / height
        snapshot, w, h = create_snapshot(
            basepath=self.type,
            source=self.attachment.path
        )
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
