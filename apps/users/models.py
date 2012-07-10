# -*- coding: utf-8 -*-
import os, datetime, settings
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=100, verbose_name=u'Имя')
    last_name = models.CharField(max_length=100, verbose_name=u'фамилия')
    phone = models.CharField(max_length=50, verbose_name=u'телефон', blank=True)
    city = models.CharField(max_length=50, verbose_name=u'город', blank=True)
    address = models.CharField(max_length=70, verbose_name=u'адрес', blank=True)
    index = models.CharField(max_length=50, verbose_name=u'индекс', blank=True)
    note = models.CharField(max_length=255, verbose_name=u'примечание', blank=True)

    class Meta:
        verbose_name =_(u'user_profile')
        verbose_name_plural =_(u'users_profiles')

    def __unicode__(self):
        return u'%s' % self.user.username

    def get_name(self):
        if self.name:
            return u'%s' % self.name
        else:
            return u'нет имени'

    def get_orders(self):
        return self.order_set.all()