from .celery import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.task(bind=True)
def echo(self, message):
    logger.info('Message: {}'.format(message))

@app.task(bind=True)
def populate_search_vectors(self, story_id):
    logger.info('story_id: {}'.format(story_id))
