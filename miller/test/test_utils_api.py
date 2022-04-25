from django.test import TestCase
from ..utils.api import reduce_dict_item_to_Q
from ..models import Document

class TestUtilsApi(TestCase):
    """
    test using docker:
    docker exec -it docker_miller_1 \
        python manage.py test \
        miller.test.test_utils_models.TestUtilsApi \
        --testrunner=miller.test.NoDbTestRunner

    test using pipenv:
    ENV=development pipenv run python manage.py test \
        miller.test.test_utils_api.TestUtilsApi \
        --testrunner=miller.test.NoDbTestRunner
    """
    def test_reduce_dict_item_to_Q(self):
        q1 = reduce_dict_item_to_Q(item={
            'Op.or': [
                {'type': 'entity'},
                {'data__type': 'portrait'}
            ]
        })
        print(str(q1))
        print(Document.objects.filter(q1).query)
        q2 = reduce_dict_item_to_Q(item={
            'Op.not': [
                {'type': 'entity'},
                {'data__type': 'portrait'}
            ]
        })
        print(str(q2))
        print(Document.objects.filter(q2).query)
        q3 = reduce_dict_item_to_Q(item={
            'Op.not': [
                {
                    'Op.or': [
                        {'type': 'entity'},
                        {'data__type': 'portrait'}
                    ]
                }
            ]
        })
        print(str(q3))
        print(Document.objects.filter(q3).query)
