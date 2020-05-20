import os
from django.test import TestCase
from django.conf import settings
from miller.utils.models import get_docs_from_json

class TestUtilsModels(TestCase):
    def test_get_docs_from_json(self):
        abs_dir_path = os.path.dirname(os.path.realpath(__file__))
        # test not found
        try:
            get_docs_from_json(
                filepath='{}/media/NOT_FOUND_documents.json'.format(abs_dir_path)
            )
        except FileNotFoundError as e:
            pass

        try:
            get_docs_from_json(
                filepath='{}/media/documents_with_duplicates.json'.format(abs_dir_path)
            )
        except ValueError as e:
            pass

        # force ignore duplicates - it takes latest element with the same slug
        docs = get_docs_from_json(
            filepath='{}/media/documents.json'.format(abs_dir_path),
            ignore_duplicates=True
        )
        print (docs)
