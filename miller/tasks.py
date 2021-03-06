from .celery import app
from django.db.models.signals import post_save
from django.dispatch import receiver
from celery.utils.log import get_task_logger
from .models import Document, Story

logger = get_task_logger(__name__)


@app.task(bind=True)
def echo(self, message):
    logger.info('Message: {}'.format(message))


@app.task(
    bind=True, autoretry_for=(Exception,), exponential_backoff=2,
    retry_kwargs={'max_retries': 5}, retry_jitter=True
)
def update_story_search_vectors(self, story_pk):
    logger.info(f'update_story_search_vectors story(pk={story_pk})')
    story = Story.objects.get(pk=story_pk)
    story.update_search_vector()
    logger.info(
        f'update_story_search_vectors story(pk={story_pk}) success.'
    )


@app.task(
    bind=True, autoretry_for=(Exception,), exponential_backoff=2,
    retry_kwargs={'max_retries': 5}, retry_jitter=True
)
def update_document_search_vectors(self, document_pk, verbose=False):
    logger.info(f'update_document_search_vectors document(pk={document_pk})')
    doc = Document.objects.get(pk=document_pk)
    doc.update_search_vector(verbose=verbose)
    logger.info(
        f'update_document_search_vectors document(pk={document_pk}) success.'
    )


@app.task(
    bind=True, autoretry_for=(Exception,), exponential_backoff=2,
    retry_kwargs={'max_retries': 5}, retry_jitter=True
)
def create_document_snapshot(self, document_pk, override=True):
    logger.info(f'create_document_snapshot document(pk={document_pk})')
    doc = Document.objects.get(pk=document_pk)
    doc.handle_preview()


@app.task(
    bind=True, autoretry_for=(Exception,), exponential_backoff=2,
    retry_kwargs={'max_retries': 5}, retry_jitter=True
)
def update_document_data_by_type(self, document_pk):
    logger.info('update_document_data_by_type document_pk: {}'.format(document_pk))
    doc = Document.objects.get(pk=document_pk)
    doc.update_data_by_type()

# listen to django signals
@receiver(post_save, sender=Document)
def document_post_save_handler(sender, instance, **kwargs):
    logger.info(f'received @post_save document_pk: {instance.pk}')
    update_document_search_vectors.delay(document_pk=instance.pk)

