from .celery import app
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
def create_document_snapshot(self, document_pk):
    logger.info('document_pk: {}'.format(document_pk))
    doc = Document.objects.get(pk=document_pk)
    doc.create_snapshot_from_attachment()
    doc.create_different_sizes_from_snapshot()


@app.task(
    bind=True, autoretry_for=(Exception,), exponential_backoff=2,
    retry_kwargs={'max_retries': 5}, retry_jitter=True)
def create_document_snapshot_images(self, document_pk):
    logger.info('document_pk: {}'.format(document_pk))
    doc = Document.objects.get(pk=document_pk)
