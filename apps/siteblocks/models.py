# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from apps.utils.managers import PublishedManager
import os, datetime
from pytils.translit import translify
from sorl.thumbnail import ImageField
from sorl.thumbnail import get_thumbnail


type_choices = (
    (u'input',u'input'),
    (u'textarea',u'textarea'),
    (u'redactor',u'redactor'),
)

class Settings(models.Model):
    title = models.CharField(
        verbose_name = u'Название',
        max_length = 150,
    )
    name = models.CharField( 
        verbose_name = u'Служебное имя',
        max_length = 250,
    )
    value = models.TextField(
        verbose_name = u'Значение'
    )
    type = models.CharField(
        max_length=20,
        verbose_name=u'Тип значения',
        choices=type_choices
    )
    class Meta:
        verbose_name =_(u'site_setting')
        verbose_name_plural =_(u'site_settings')

    def __unicode__(self):
        return u'%s' % self.name

def file_path_Product(instance, filename):
    return os.path.join('images','banners',  translify(filename).replace(' ', '_') )

class Banner(models.Model):
    title = models.CharField(u'название',max_length = 150,)
    image = models.FileField(
        upload_to=file_path_Product,
        #help_text=u'Размер баннера 180х180 пикс.',
        verbose_name = u'картинка',
    )
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        verbose_name = _(u'banner')
        verbose_name_plural = _(u'banners')

    def __unicode__(self):
        return self.title

    def get_src_image(self):
        return self.image.url

    def banner_preview(self):
        image = self.image
        if image:
            im = get_thumbnail(self.image, '96x96', crop='center', quality=99)
            return u'<span><img src="%s" width="96" height="96"></span>' %im.url
        else:
            return u'<span></span>'
    banner_preview.allow_tags = True
    banner_preview.short_description = u'Превью'