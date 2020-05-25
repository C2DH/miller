import os
from django.test import TestCase
from miller.utils.models import get_docs_from_json, get_cache_key


class TestUtilsModels(TestCase):
    """
    test using docker:
    docker exec -it docker_miller_1 \
        python manage.py test \
        miller.test.test_utils_models.TestUtilsModels \
        --testrunner=miller.test.NoDbTestRunner
    """
    def test_get_docs_from_json(self):
        abs_dir_path = os.path.dirname(os.path.realpath(__file__))
        # test not found
        try:
            get_docs_from_json(
                filepath=F'{abs_dir_path}/media/NOT_FOUND_documents.json'
            )
        except FileNotFoundError:
            pass

        try:
            get_docs_from_json(
                filepath=F'{abs_dir_path}/media/documents_with_duplicates.json'
            )
        except ValueError:
            pass

        # force ignore duplicates - it takes latest element with the same slug
        docs = get_docs_from_json(
            filepath=F'{abs_dir_path}/media/documents.json',
            ignore_duplicates=True
        )
        print(docs)
        docs = get_docs_from_json(
            filepath=F'{abs_dir_path}/media/documents-flatten.json',
            ignore_duplicates=True,
            expand_flatten_data=True
        )
        print(docs)

    def test_get_cache_key(self):
        self.assertEquals(
            'document.32.extra',
            get_cache_key(model='document', pk=32, extra='extra'),
        )
