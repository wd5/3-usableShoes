# -*- coding: utf-8 -*-
from django.db import models
from sorl.thumbnail.fields import ImageField
import os
from pytils.translit import translify


from pytils.translit import translify

def get_doc_path(instance, filename):
    return os.path.join(instance.get_upload_path(filename),
                 instance.get_upload_filename(filename))


class AbstractFile(models.Model):
    title = models.CharField(
        verbose_name = u'название',
        max_length = 250,
    )
    size = models.IntegerField(
        verbose_name = u'размер',
        editable = False,
        default = 0,
    )
    order = models.PositiveIntegerField(
        verbose_name = u'сортировка',
        default = 10,
    )
    class Meta:
        abstract = True
        ordering = ['-order',]

    def save(self, **kwargs):
        self.title = self.title.strip()
        self.size = self._get_file_size()
        super(AbstractFile, self).save(**kwargs)

    def _get_file_size(self):
        try:
            return self.file.size
        except:
            pass
        return 0

    def get_upload_path(self, filename):
        raise NotImplementedError

    def get_upload_filename(self, filename):
        return translify(filename).replace(' ', '_')

    @property
    def ext(self):
        try:
            return os.path.splitext(self.filename_with_ext)[1][1:].lower()
        except:
            pass
        return u''

    @property
    def filename(self):
        try:
            return os.path.splitext(self.filename_with_ext)[0]
        except:
            pass
        return u''

    @property
    def filename_with_ext(self):
        try:
            return os.path.basename(self.file.name)
        except TypeError, AttributeError:
            pass
        return u''

class BaseDoc(AbstractFile):
    file = models.FileField(
        verbose_name = u'файл',
        upload_to = get_doc_path,
    )
    class Meta:
        abstract = True

class BasePic(AbstractFile):
    file = ImageField(
        verbose_name = u'файл',
        upload_to = get_doc_path,
    )
    class Meta:
        abstract = True