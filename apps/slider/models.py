# -*- coding: utf-8 -*-
import os, datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models

from pytils.translit import translify
from sorl.thumbnail import ImageField  as sorl_ImageField, get_thumbnail

from apps.utils.managers import PublishedManager
from apps.utils.models import ImageCropMixin

class ImageField(sorl_ImageField, models.ImageField):
    pass



def file_path(instance, filename):
    return os.path.join('images','slider',  translify(filename).replace(' ', '_') )

class Slider(ImageCropMixin, models.Model):
    image = ImageField(verbose_name=u'Картинка', upload_to=file_path)
    title = models.CharField(verbose_name=u'Название', max_length="255",)
    link = models.CharField(verbose_name=u'ссылка', max_length="255",)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)
    
    crop_size = [300, 200]

    objects = PublishedManager()

    class Meta:
        verbose_name = u'слайдер'
        verbose_name_plural = u'слайдеры'
        ordering = ['-order',]

    def __unicode__(self):
        return self.title

    def admin_photo_preview(self):
        image = self.image
        if image:
            im = get_thumbnail(self.image, '96x96', crop='center', quality=99)
            return u'<span><img src="%s" width="96" height="96"></span>' %im.url
        else:
            return u'<span></span>'
    admin_photo_preview.allow_tags = True
    admin_photo_preview.short_description = u'Превью'