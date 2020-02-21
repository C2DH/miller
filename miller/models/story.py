import os
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import Document
from . import Author
from . import Tag
from ..utils import get_user_path
from ..fields import UTF8JSONField

from ..tasks import populate_search_vectors

def get_owner_path(instance, filename, safeOrigin=False):
    root, ext = os.path.splitext(filename)
    src = os.path.join(
        get_user_path(user=instance.owner),
        f"{instance.short_url}{ext}",
    )
    return src

class Story(models.Model):
    DRAFT    = 'draft'   # visible just for you and staff users
    SHARED   = 'shared'  # share with specific user
    PUBLIC   = 'public'  # everyone can access that.
    # status related to review process.
    PENDING      = 'pending'
    EDITING      = 'editing' # only staff and editors access this
    REVIEW       = 'review'  # staff, editors and reviewer acces this
    REVIEW_DONE  = 'reviewdone'
    PRE_PRINT    = 'preprint' # in this status and whenever is public, we ask the author to comment his commit on each save to better trace history

    DELETED  = 'deleted' # will be sent to the bin

    STATUS_CHOICES = (
        (DRAFT,   'draft'),
        (SHARED,  'shared'),
        (PUBLIC,  'public'),  # accepted paper.
        (DELETED, 'deleted'),

        (PENDING,     'pending review'),  # ask for publication, pending review
        (EDITING,     'editing'), # ask for editing review
        (REVIEW,      'review'),             # under review
        (REVIEW_DONE, 'review done'),
        (PRE_PRINT,   'pre print')
    )

    short_url = models.CharField(max_length=22, db_index=True, unique=True)

    title     = models.CharField(max_length=500)
    slug      = models.CharField(max_length=140, unique=True, blank=True, db_index=True) # force the unicity of the slug (story lookup from the short_url)
    abstract  = models.CharField(max_length=2000, blank=True, null=True)
    data      = UTF8JSONField(verbose_name=u'metadata contents', help_text='JSON format', default=dict, blank=True)

    date               = models.DateTimeField(db_index=True, blank=True, null=True) # date displayed (metadata)
    date_created       = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    status    = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT, db_index=True)
    priority  = models.PositiveIntegerField(default=0, db_index=True)

    owner     = models.ForeignKey(User, on_delete=models.CASCADE); # at least the first author, the one who owns the file.

    authors   = models.ManyToManyField(Author, related_name='stories', blank=True) # collaborators
    documents = models.ManyToManyField(Document, related_name='stories', through='Caption', blank=True)

    stories   = models.ManyToManyField("self", through='Mention', symmetrical=False, related_name='mentioned_to')

    # store the git hash for current gitted self.contents. Used for comments.
    version   = models.CharField(max_length=22, default='', help_text='store the git hash for current gitted self.contents.', blank=True)

    # the leading document(s), e.g. an interview
    covers = models.ManyToManyField(Document, related_name='covers', blank=True)

    tags      = models.ManyToManyField(Tag, blank=True) # tags

    # cover thumbnail, e.g. http://www.eleganzadelgusto.com/wordpress/wp-content/uploads/2014/05/Marcello-Mastroianni-for-Arturo-Zavattini.jpg
    cover = models.URLField(max_length=500, blank=True, null=True)

    # cover copyright or caption, markdown flavoured. If any
    cover_copyright = models.CharField(max_length=140, blank=True, null=True)

    # fileField
    source = models.FileField(upload_to=get_owner_path, blank=True, null=True)

    # fileField (usually a zotero-friendly importable file)
    bibliography = models.FileField(upload_to=get_owner_path, blank=True, null=True)

    # add huge search field
    search_vector = SearchVectorField(null=True, blank=True)


    def __str__(self):
        return self.slug

@receiver(post_save, sender=Story)
def story_populate_search_vectors(sender, instance, **kwargs):
    populate_search_vectors.delay(story_id=instance.pk)
