from .celery import app
from celery.utils.log import get_task_logger
from .models import Document

logger = get_task_logger(__name__)

@app.task(bind=True)
def echo(self, message):
    logger.info('Message: {}'.format(message))

@app.task(bind=True)
def populate_search_vectors(self, story_id):
    logger.info('story_id: {}'.format(story_id))

@app.task(bind=True, autoretry_for=(Exception,), exponential_backoff=2, retry_kwargs={'max_retries': 5}, retry_jitter=True)
def create_document_snapshot(self, document_pk):
    logger.info('document_pk: {}'.format(document_pk))
    doc = Document.objects.get(pk=document_pk)
    doc.create_snapshot_from_attachment()

@app.task(bind=True, autoretry_for=(Exception,), exponential_backoff=2, retry_kwargs={'max_retries': 5}, retry_jitter=True)
def create_document_snapshot_images(self, document_pk):
    logger.info('document_pk: {}'.format(document_pk))
    doc = Document.objects.get(pk=document_pk)
