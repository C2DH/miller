import os
import logging
from wand.image import Image
from django.test import TestCase
from miller.snapshots import resize_wand_image, create_snapshot
from miller.snapshots import create_different_sizes_from_snapshot


logger = logging.getLogger(__name__)
abs_dir_path = os.path.dirname(os.path.realpath(__file__))
image_licence = '''
    "File:PDP-8L on ICS Astrotype system.jpg" by AstrotypeSystem.jpg:
    Douglas W. Jones derivative work: User:Clusternote
    is licensed under CC0 1.0
'''


class TestSnapshots(TestCase):
    """
    test using docker:
    docker exec -it docker_miller_1 \
        python manage.py test \
        miller.test.test_snapshots.TestSnapshots \
        --testrunner=miller.test.NoDbTestRunner
    """
    def test_create_snapshot(self):
        attachment = f'{abs_dir_path}/media/PDP-8L_on_ICS_Astrotype_system.jpg'
        logger.info(image_licence)
        snapshot, w, h = create_snapshot(basepath='test', source=attachment)
        self.assertTrue(os.path.exists(snapshot))

        # create corresponding sizes:
        sizes = create_different_sizes_from_snapshot(
            snapshot=snapshot,
            sizes=[
                ('thumbnail', [72, 0, 260, 0]),
                ('preview', [96, 0, 0, 800]),
                ('preview-constraint', [96, 800, 0, 0])
            ],
            format='jpg',
            data_key='resolutions'
        )
        self.assertEquals(260, sizes['resolutions']['thumbnail']['width'])
        self.assertEquals(131, sizes['resolutions']['thumbnail']['height'])
        self.assertEquals(
            'test/snapshots/PDP-8L_on_ICS_Astrotype_system-96-0-0-800.jpg',
            sizes['resolutions']['preview']['url']
        )
        self.assertEquals(1592, sizes['resolutions']['preview']['width'])
        self.assertEquals(800, sizes['resolutions']['preview']['height'])
        self.assertEquals(
            'test/snapshots/PDP-8L_on_ICS_Astrotype_system-72-0-260-0.jpg',
            sizes['resolutions']['thumbnail']['url']
        )
        self.assertEquals(800, sizes['resolutions']['preview-constraint']['width'])
        self.assertEquals(402, sizes['resolutions']['preview-constraint']['height'])
        self.assertEquals(
            'test/snapshots/PDP-8L_on_ICS_Astrotype_system-96-800-0-0.jpg',
            sizes['resolutions']['preview-constraint']['url']
        )

    def test_resize_wand_image(self):
        attachment = f'{abs_dir_path}/media/PDP-8L_on_ICS_Astrotype_system.jpg'
        logger.info(image_licence)

        with Image(filename=attachment) as img:
            # no resize :)
            resizedImg, w, h = resize_wand_image(
                img, max_size=None,
                set_width=None,
                set_height=None
            )
            self.assertEquals(h, 792)
            self.assertEquals(w, 1576)

            # set width
            resizedImg, w, h = resize_wand_image(
                img, max_size=None, set_width=300, set_height=None)
            self.assertEquals(w, 300)
            self.assertEquals(h, 151)
            # resizedImg.save(filename='{}.resized.jpg'.format(attachment))

            # set height
            resizedImg, w, h = resize_wand_image(
                img, max_size=None, set_width=None, set_height=300)
            self.assertEquals(h, 300)
            self.assertEquals(w, 596)
            # resizedImg.save(filename='{}.resized-h.jpg'.format(attachment))

            # set maximum dimension, ignore other params
            resizedImg, w, h = resize_wand_image(
                img, max_size=500, set_width=300, set_height=300)
            self.assertEquals(w, 500)
            self.assertEquals(h, 252)
            # resizedImg.save(filename='{}.resized-ms.jpg'.format(attachment))
