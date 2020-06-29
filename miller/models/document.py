import os
import logging
from django.conf import settings
from django.db import models
from django.db import connection
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.auth.models import User
from ..fields import UTF8JSONField
from ..snapshots import create_snapshot, create_different_sizes_from_snapshot
from ..utils.models import get_search_vector_query, create_short_url
from ..utils.media import get_video_subtitles


logger = logging.getLogger(__name__)


def attachment_file_name(instance, filename):
    return os.path.join(instance.type, filename)


def private_attachment_file_name(instance, filename):
    return os.path.join(settings.MEDIA_PRIVATE_ROOT, instance.type, filename)


def snapshot_attachment_file_name(instance, filename):
    return os.path.join(instance.type, 'snapshots', filename)


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
        (AUDIO, 'audio'),
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

    copyrights = models.TextField(null=True, blank=True, default='')

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

    # enable full text search using postgres vectors
    allow_fulltext_search = True

    class Meta:
        indexes = [GinIndex(fields=['search_vector'])]

    def __str__(self):
        return self.slug

    def create_snapshot_from_attachment(self, override=True):
        """
        if there is an attachment, generate a PNG snapshot or similar.
        If snapshot is already present, look for override param
        """
        logger.info(
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
                f'create_snapshot_from_attachment document pk:{self.pk} '
                f'failed, attached file {self.attachment.path} does not exist.'
            )
            return
        # get snaphot path and its width / height
        snapshot, w, h = create_snapshot(
            basepath=self.type,
            source=self.attachment.path
        )
        # save document, snapshot should be related to MEDIA_ROOT
        self.snapshot = os.path.join(*snapshot.replace(
            settings.MEDIA_ROOT, ''
        ).split('/'))
        self.data.update({
            'snapshot': {
                'width': w,
                'height': h
            }
        })
        logger.info(
            f'create_snapshot_from_attachment document pk:{self.pk}'
            f' using file {self.attachment.path}'
            f' success: created {self.snapshot.path}'
        )
        self.save()

    def create_different_sizes_from_snapshot(self, data_key='resolutions'):
        if not self.snapshot or not getattr(self.snapshot, 'path', None):
            logger.error(
                f'generate_other_images_from_snapshot document pk:{self.pk}'
                f' failed, no snapshot found! Skip.')
            return
        if not os.path.exists(self.snapshot.path):
            logger.error(
                f'generate_other_images_from_snapshot document pk:{self.pk} '
                f'failed, snapshot file {self.snapshot.path} does not exist.'
            )
            return
        sizes = create_different_sizes_from_snapshot(
            snapshot=self.snapshot.path,
            sizes=[
                ('preview', settings.MILLER_SIZES_SNAPSHOT_PREVIEW),
                ('thumbnail', settings.MILLER_SIZES_SNAPSHOT_THUMBNAIL),
                ('medium', settings.MILLER_SIZES_SNAPSHOT_MEDIUM),
            ],
            format='jpg',
            data_key=data_key,
            media_url=settings.MEDIA_URL
        )
        self.data.update(sizes)
        self.save()

    def handle_preview(self, override=False):
        """
        Create a preview images according to the settings.
        """
        if not self.snapshot or not getattr(self.snapshot, 'path', None):
            if os.path.exists(self.attachment.snapshot):
                logger.info(f'handle_preview document pk:{self.pk} skip snapshot generation, snapshot file found')
            elif override:
                logger.info(f'handle_preview document pk:{self.pk} has a INVALID snapshot, override')
                self.create_snapshot_from_attachment()
        elif override:
            logger.info(f'handle_preview pk:{self.pk}) creating snapshot...')
            self.create_snapshot_from_attachment()
        self.create_different_sizes_from_snapshot()

    def update_data_by_type(self):
        """
        update data.source according to multilingual settings if multilanguage version of the attachment are dfounf
        for video add subtitles section:
            "subtitles": [
                {
                    type: "vtt",
                    language: "de_DE",
                    url: "/video/{slug}.de_DE.vtt"
                }
            ]
        for images
        """
        if self.type == Document.VIDEO:
            subtitles = get_video_subtitles(path_prefix=f'{self.type}/{self.slug}')
            self.data.update(subtitles)
        self.save()

    def update_search_vector(self, verbose=False):
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
            verbose=verbose
        )
        if not contents:
            logger.error(
                f'update_search_vector failed for document:{self.pk} (empty?)'
            )
            return
        if verbose:
            logger.info(
                f'VERBOSE - contents: {contents}'
            )
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

    