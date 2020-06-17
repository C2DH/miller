# Modle dedicated to snapshot generation
import os
import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from wand.image import Image, Color

logger = logging.getLogger(__name__)


def _get_or_create_snapshots_folder(basepath='image'):
    """
    Generate a folder in order to store snapshots. below MEDIA_ROOT according to file type
    """
    snapshots_path = os.path.join(settings.MEDIA_ROOT, basepath, 'snapshots')
    try:
        os.makedirs(snapshots_path)
    except OSError:
        # directory exists, pass .
        pass
    return snapshots_path


def resize_wand_image(img, max_size=None, set_width=None, set_height=None):
    """
    Given a wand.image instance, this method returns the resized wand.Image
    """
    w = img.width
    h = img.height
    ratio = 1.0 * w / h
    logger.info("resize_wand_image from: {}w {}h ratio{}".format(w, h, ratio))
    if max_size:
        if img.width > img.height:
            w = max_size
            h = round(w / ratio)
        elif img.width < img.height:
            h = max_size
            w = round(ratio * h)
        else:
            # squared image
            h = w = max_size
    elif set_width and set_height:
        h = set_height
        w = set_width
    elif set_width:
        w = set_width
        h = round(w / ratio)
    elif set_height:
        h = set_height
        w = round(ratio * h)
    img.transform(resize='%sx%s' % (w, h))
    return img, w, h


def create_snapshot(
    basepath, source, dest=None, mimetype=None, format='jpg', **options
):
    """
    "Snapshot" is a JPG image, normally medium resolution of whatever source file is.
    Generate snapshot from filepath using current settings.MILLER_SIZES_SNAPSHOT
    Usage:

        snapshot_filepath = create_snapshot('image', source='/path/to/file.pdf')

    THis will return the filepath of the image created, or raise exception otherwise
    """
    # output file
    snapshot = dest if dest else os.path.join(
        _get_or_create_snapshots_folder(basepath),
        '{}.{}'.format(Path(source).stem, format)
    )
    # guess mimetype. If mimetype cannot be guessed. raise an error
    source_mimetype, encoding = (mimetype, None) if mimetype else mimetypes.guess_type(
        source, strict=True
    )

    resolution, max_size, set_width, set_height = settings.MILLER_SIZES_SNAPSHOT
    logger.info(
        f'create_snapshot with resolution:{resolution}, max_size:{max_size},'
        f' set_width:{set_width}, set_height:{set_height},'
        f' source_mimetype: {source_mimetype}'
    )

    if source_mimetype == 'application/pdf':
        page = options.get('pdf_page', 1)
        alpha_channel = options.get('pdf_alpha_channel', 'remove')
        background_color = options.get('pdf_background_color', 'white')
        with Image(filename=f'{source}[{page}]', resolution=resolution) as img:
            img.format = format
            # Set white background by default
            img.background_color = Color(background_color)
            img.alpha_channel = alpha_channel
            # img.compression_quality = compression_quality
            img.resolution = (resolution, resolution)
            img, w, h = resize_wand_image(
                img=img, max_size=max_size,
                set_width=set_width, set_height=set_height
            )
            img.save(filename=snapshot)
    else:
        try:
            with Image(filename=source, resolution=resolution) as img:
                img.format = format
                resizedImg, w, h = resize_wand_image(
                    img=img, max_size=max_size,
                    set_width=set_width, set_height=set_height
                )
                img.save(filename=snapshot)
        except Exception as e:
            logger.exception(e)
            w = 0
            h = 0

    return snapshot, w, h


def create_different_sizes_from_snapshot(
    snapshot,
    sizes=[
        ('preview', settings.MILLER_SIZES_SNAPSHOT_PREVIEW),
        ('thumbnail', settings.MILLER_SIZES_SNAPSHOT_THUMBNAIL),
        ('medium', settings.MILLER_SIZES_SNAPSHOT_MEDIUM),
    ],
    format='jpg',
    data_key=settings.MILLER_SIZES_SNAPSHOT_DATA_KEY,
    media_root=settings.MEDIA_ROOT,
    media_url=None
):
    data_values = {}

    for key, size in sizes:
        resolution, max_size, set_width, set_height = size
        dest = '-'.join((
            snapshot.rsplit('.', 1)[0],
            f'{resolution}-{max_size}-{set_width}-{set_height}.{format}'
        ))
        # dest_url must be relative to MEDIA_ROOT
        dest_url = os.path.join(*dest.replace(
            media_root, ''
        ).split('/'))
        if media_url:
            dest_url = os.path.join(media_url, dest_url)

        logger.info(
            f'generate_other_images_from_snapshot'
            f' settings: {key}, resolution:{resolution}, max_size:{max_size},'
            f' set_width:{set_width}, set_height:{set_height}'
            f' dest: {dest}'
            f' dest_url: {dest_url}'
        )
        with Image(filename=snapshot, resolution=resolution) as img:
            img.format = format
            resizedImg, w, h = resize_wand_image(
                img=img, max_size=max_size,
                set_width=set_width, set_height=set_height
            )
            img.save(filename=dest)
            data_values.update({
                key: {
                    'width': w,
                    'height': h,
                    'url': dest_url
                }
            })

    return {data_key: data_values}
