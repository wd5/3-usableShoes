# -*- coding: utf-8 -*-
DATABASE_NAME = u'usableShoes'
PROJECT_NAME = u'practiceshoes'
SITE_NAME = u'Практичная обувь'
DEFAULT_FROM_EMAIL = u'support@practiceshoes.ru'

from config.base import *

try:
    from config.development import *
except ImportError:
    from config.production import *

TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'apps.siteblocks',
    'apps.pages',
    'apps.faq',
    'apps.products',
    'apps.users',
    'apps.spam',
    'apps.orders',

    'sorl.thumbnail',
    #'south',
    #'captcha',
)

#AUTHENTICATION_BACKENDS = (
#    'apps.auth_backends.CustomUserModelBackend',
#)

MIDDLEWARE_CLASSES += (
    'apps.pages.middleware.PageFallbackMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'apps.pages.context_processors.meta',
    'apps.siteblocks.context_processors.settings',
    'apps.utils.context_processors.authorization_form',
)