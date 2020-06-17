import os
from django.conf import settings

def get_video_subtitles(
    path_prefix,  # e.g. video/slug-of-the-video
    data_key=settings.MILLER_VIDEO_SUBTITLES_DATA_KEY,
    types=settings.MILLER_VIDEO_SUBTITLES_TYPES
):
    """
    source it's the path relative to settings.MEDIA_ROOT
    """
    data_values = []
    for ext in types:
        for c, t, language_code, s in settings.MILLER_LANGUAGES:
            subtitle_name = f'{path_prefix}.{language_code}.{ext}'
            subtitle_url = f'{settings.MEDIA_URL}{subtitle_name}'
            subtitle_filepath = os.path.join(
                settings.MEDIA_ROOT,
                subtitle_name
            )
            is_subtitle_available = os.path.exists(subtitle_filepath)
            data_values.append({
                'type': ext,
                'language': language_code,
                'url': subtitle_url,
                'availability': is_subtitle_available,
            })
    return {data_key: data_values}
