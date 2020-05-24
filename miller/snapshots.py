# Modle dedicated to snapshot generation
import os, logging, mimetypes
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
            #squared image
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
    img.transform(resize='%sx%s'% (w, h))
    return img, w, h


def create_snapshot(basepath, source, dest=None, mimetype=None, format='jpg', **options):
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
    source_mimetype, encoding = (mimetype, None) if mimetype else mimetypes.guess_type(source, strict=True)

    resolution, max_size, set_width, set_height = settings.MILLER_SIZES_SNAPSHOT
    logger.info('create_snapshot with resolution:{}, max_size:{}, set_width:{}, set_height:{}, source_mimetype: {}'.format(
        resolution, max_size, set_width, set_height, source_mimetype
    ))

    if source_mimetype == 'application/pdf':
        page = options.get('pdf_page', 1)
        alpha_channel = options.get('pdf_alpha_channel', 'remove')
        background_color = options.get('pdf_background_color', 'white')
        with Image(filename='{source}[{page}]'.format(source=source, page=page), resolution=resolution) as img:
            img.format = format
            img.background_color = Color(background_color) # Set white background.
            img.alpha_channel = alpha_channel
            # img.compression_quality = compression_quality
            img.resolution = (resolution, resolution)
            img,w,h = resize_wand_image(img=img, max_size=max_size, set_width=set_width, set_height=set_height)
            img.save(filename=snapshot)
    else:
        with Image(filename=source, resolution=resolution) as img:
            img.format = format
            resizedImg, w, h = resize_wand_image(img=img, max_size=max_size, set_width=set_width, set_height=set_height)
            img.save(filename=snapshot)

    return snapshot,w,h

#
# def generate_other_images_from_snapshot(filename, output, width=None, height=None, crop=False, resolution=72, max_size=None, compression_quality=95, progressive=False):
#       """
#       Use liquid_rescale to scale down snapshots to the desired dimension.
#       params key defines a data field to be updated with new properties.
#       @param fit maximum dimension in width OR height
#       """
#       from wand.image import Image
#
#       # clean
#       try:
#         os.remove(output)
#       except OSError as e:
#         pass
#
#       try:
#         os.makedirs(os.path.dirname(output))
#       except OSError:
#         pass
#
#       print("resolution: {}, filename: {}".format(resolution, filename))
#       d = {}
#
#       if not width and not height and not max_size:
#         raise Exception('At least one dimension should be provided, width OR height OR size')
#
#       with Image(filename=filename, resolution=resolution) as img:
#         print("dimensions: {}, {}".format(img.width, img.height))
#         ratio = 1.0*img.width/img.height
#         d['width']  = img.width
#         d['height'] = img.height
#         if max_size:
#           if img.width > img.height:
#             width = max_size
#             height = width / ratio
#           elif img.width < img.height:
#             height = max_size
#             width = ratio * height
#           else: #squared image
#             height = width = max_size
#         # resize to the minimum, then crop
#         elif not height:
#           height = width / ratio
#         elif not width:
#           width = ratio * height
#
#         d['snapshot_width']  = width
#         d['snapshot_height'] = height
#
#         if not crop:
#           img.transform(resize='%sx%s'% (width, height))
#         else:
#           # print 'ici', img.width, img.height
#           if img.width > img.height :
#             # width greated than height
#             img.transform(resize='x%s'%width)
#           elif img.width < img.height:
#             # print 'ici', img.width, img.height
#             img.transform(resize='%sx'%height)
#           else:
#             img.transform(resize='%sx%s'% (width, height))
#           img.crop(width=width, height=height, gravity='center')
#
#
#         d['thumbnail_width']  = img.width
#         d['thumbnail_height'] = img.height
#
#
#         img.resolution = (resolution, resolution)
#         img.compression_quality = compression_quality
#
#         if progressive:
#           img.format = 'pjpeg'
#         img.save(filename=output)
#         return d
