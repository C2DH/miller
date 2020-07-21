"""miller URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from rest_framework import routers
from .api.story import StoryViewSet
from .api.document import DocumentViewSet
from .api.profile import ProfileViewSet
from .api.mention import MentionViewSet
from .api.caption import CaptionViewSet
from .api.tag import TagViewSet
from . import __version__

router = routers.DefaultRouter(trailing_slash=True)
router.register(r'story', StoryViewSet)
router.register(r'document', DocumentViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'mention', MentionViewSet)
router.register(r'caption', CaptionViewSet)
router.register(r'tag', TagViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    path('admin/', admin.site.urls),
    # oaht2 toolkit here
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

admin.site.site_header = mark_safe(
    '<b style="color:white">Miller</b>'
    f' &middot {settings.MILLER_GIT_TAG}{__version__}'
    f' ({settings.MILLER_GIT_BRANCH}/{settings.MILLER_GIT_REVISION})'
)

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
