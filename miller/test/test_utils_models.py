import os
from django.test import TestCase
from miller.utils.models import get_docs_from_json, get_cache_key
from miller.utils.models import get_search_vector_query
from miller.models import Document


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
        # print(docs)
        docs = get_docs_from_json(
            filepath=F'{abs_dir_path}/media/documents-flatten.json',
            ignore_duplicates=True,
            expand_flatten_data=True
        )
        # print(docs)

    def test_get_cache_key(self):
        self.assertEquals(
            'document.32.extra',
            get_cache_key(model='document', pk=32, extra='extra'),
        )

    def test_get_search_vector_query(self):
        doc = Document(pk=1, slug='with-vectors', title='documen title', data={
            "type": "Other",
            "end_date": "1990-01-01",
            "start_date": "1990-01-02",
            "year": 2018,
            "download": False,
            "title": {
                "de_DE": "EUTELSAT",
                "fr_FR": "EUTELSAT"
            },
            "description": {
                "de_DE": "Finaler Bericht von Gaston Bohnenberger und ...",
                "fr_FR": "Rapport final de Guy Modert et Gaston .."
            }
        })
        q, contents = get_search_vector_query(
            doc,
            languages=[
                ('en', 'British English', 'en_GB', 'english'),
                ('fr', 'French', 'fr_FR', 'french'),
                ('de', 'German', 'de_DE', 'german'),
            ],
            simple_fields=[
                ('pk', 'A', 'simple'),
                ('slug', 'A', 'simple'),
                ('title', 'A', 'simple'),
            ],
            multilanguage_fields=[
                ('title', 'A'),
                ('description', 'B')
            ],
        )
        self.assertEquals(contents, [
            (1, 'A', 'simple'),
            ('with-vectors', 'A', 'simple'),
            ('documen title', 'A', 'simple'),
            ('EUTELSAT', 'A', 'french'),
            ('EUTELSAT', 'A', 'german'),
            ('Rapport final de Guy Modert et Gaston ..', 'B', 'french'),
            ('Finaler Bericht von Gaston Bohnenberger und ...', 'B', 'german')
        ])
        self.assertEquals(
            q,
            "setweight(to_tsvector(COALESCE(%s,'')), 'A') || "
            "setweight(to_tsvector(COALESCE(%s,'')), 'A') || "
            "setweight(to_tsvector(COALESCE(%s,'')), 'A') || "
            "setweight(to_tsvector('french',COALESCE(%s,'')), 'A') || "
            "setweight(to_tsvector('german',COALESCE(%s,'')), 'A') || "
            "setweight(to_tsvector('french',COALESCE(%s,'')), 'B') || "
            "setweight(to_tsvector('german',COALESCE(%s,'')), 'B')"
        )
