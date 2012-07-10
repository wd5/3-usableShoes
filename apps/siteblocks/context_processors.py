# -*- coding: utf-8 -*-
from apps.siteblocks.models import Settings
from settings import SITE_NAME

def settings(request):
    try:
        delivery = Settings.objects.get(name='delivery_block').value
    except Settings.DoesNotExist:
        delivery = False

    return {
        'delivery': delivery,
        'site_name': SITE_NAME,
    }