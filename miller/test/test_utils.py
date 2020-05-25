import os
from django.test import TestCase
from django.conf import settings
from miller.utils import get_data_from_dict

class TestUtils(TestCase):
    def test_get_data_from_dict(self):
        print('testiiii')
        data = get_data_from_dict({
            'data__title__fr_FR': 'un joli title',
            'data__title__en_GB': 'A nicer title',
        })
        # {'data': {'title': {'fr_FR': 'un joli title', 'en_GB': 'A nicer title'}}}
        self.assertEquals(data['data']['title']['fr_FR'], 'un joli title')
        self.assertEquals(data['data']['title']['en_GB'], 'A nicer title')

        # should work nicely with 0 padded values, 1917-05-21 or with Date(1917,4,21)
        # or with excel formatted dates (1900 Date format)
        data = get_data_from_dict({
            'data__title__fr_FR': 'un très joli title',
            'data__start_date': '1917-05-21',
            'data__end_date': 'Date(1917,4,21)',
            'data__peak_date': '1917-05-21',
            'data__excel__digit_date': 43411,
            'data__excel__digit_date_as_string': '43411',
            'data__excel__digit_date_as_float': 43411.322,
        }, datetime_suffix=(
            'start_date', 'end_date', 'peak_date',
            'digit_date', 'digit_date_as_string', 'digit_date_as_float',
        ))
        self.assertEquals(data['data']['title']['fr_FR'], 'un très joli title')
        self.assertEquals(data['data']['start_date'], '1917-05-21T00:00:00')
        self.assertEquals(data['data']['end_date'], '1917-05-21T00:00:00')
        self.assertEquals(data['data']['peak_date'], '1917-05-21T00:00:00')
        self.assertEquals(data['data']['excel']['digit_date'], '2018-11-07T00:00:00')
        self.assertEquals(data['data']['excel']['digit_date_as_string'], '2018-11-07T00:00:00')
        self.assertEquals(data['data']['excel']['digit_date_as_float'], '2018-11-07T07:43:40.800000')
