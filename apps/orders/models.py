# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from apps.products.models import Product, Size
from apps.users.models import Profile
import datetime
import os

class Cart(models.Model):
    profile = models.OneToOneField(Profile, verbose_name=u'Профиль', blank=True, null=True)
    create_date = models.DateTimeField(verbose_name=u'Дата создания', default=datetime.datetime.now)
    sessionid = models.CharField(max_length=50, verbose_name=u'ID сессии', blank=True, )

    class Meta:
        verbose_name = _(u'cart')
        verbose_name_plural = _(u'carts')

    def __unicode__(self):
        return u'%s - %s' % (self.sessionid, self.create_date)

    def get_products(self):
        return CartProduct.objects.select_related().filter(cart=self, is_deleted=False)

    def get_products_all(self):
        return CartProduct.objects.select_related().filter(cart=self)

    def get_products_count(self):
        count = 0
        for item in self.get_products():
            count += item.count
        return count
        #return self.get_products().count()

    def get_total(self):
        sum = 0
        for cart_product in self.cartproduct_set.select_related().filter(is_deleted=False):
            sum += cart_product.get_total()
        return sum

    def get_str_total(self):
        total = self.get_total()
        value = u'%s' % total
        try:
            if total._isinteger():
                value = u'%s' % value[:len(value) - 3]
                count = 3
            else:
                count = 6
        except AttributeError:
            return value

        if len(value) > count:
            ends = value[len(value) - count:]
            starts = value[:len(value) - count]

            return u'%s %s' % (starts, ends)
        else:
            return value


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=u'Корзина')
    count = models.PositiveIntegerField(default=1, verbose_name=u'Количество')
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    is_deleted = models.BooleanField(verbose_name=u'удалён', default=False)

    class Meta:
        ordering = ['is_deleted','product__title']
        verbose_name = _(u'product_item')
        verbose_name_plural = _(u'product_items')

    def get_total(self):
        total = self.product.price * self.product.count * self.count
        return total

    def get_str_total(self):
        total = self.get_total()
        value = u'%s' % total
        if total._isinteger():
            value = u'%s' % value[:len(value) - 3]
            count = 3
        else:
            count = 6

        if len(value) > count:
            ends = value[len(value) - count:]
            starts = value[:len(value) - count]

            return u'%s %s' % (starts, ends)
        else:
            return value

    def __unicode__(self):
        return u'на %s руб.' % self.get_str_total()

from django.db.models.signals import post_save

def delete_old_carts(sender, instance, created, **kwargs):
    if created:
        now = datetime.datetime.now()
        day_ago30 = now - datetime.timedelta(days=30)
        carts = Cart.objects.filter(create_date__lte=day_ago30)
        if carts:
            carts.delete()

post_save.connect(delete_old_carts, sender=CartProduct)

order_carting_choices = (
    (u'moscow', u'Доставка по Москве'),
    (u'country', u'Доставка по стране'),
    (u'selfcarting', u'Самовывоз'),
    )

order_status_choices = (
    (u'processed', u'Обрабатывается'),
    (u'posted', u'Отправлен'),
    (u'delivered', u'Доставлен'),
    (u'cancelled', u'Отменен'),
    )

class Order(models.Model):
    profile = models.ForeignKey(Profile, verbose_name=u'Профиль', blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name=u'Имя')
    last_name = models.CharField(max_length=100, verbose_name=u'фамилия')
    email = models.EmailField(verbose_name=u'E-mail',max_length=75)
    phone = models.CharField(max_length=50, verbose_name=u'телефон')

    order_carting = models.CharField(max_length=30, verbose_name=u'Тип доставки', choices=order_carting_choices, )
    order_status = models.CharField(max_length=30, verbose_name=u'Статус заказа', choices=order_status_choices, )

    city = models.CharField(max_length=50, verbose_name=u'город', blank=True)
    address = models.CharField(max_length=70, verbose_name=u'адрес', blank=True)
    index = models.CharField(max_length=50, verbose_name=u'индекс', blank=True)
    note = models.CharField(max_length=255, verbose_name=u'примечание', blank=True)

    create_date = models.DateTimeField(verbose_name=u'Дата оформления', default=datetime.datetime.now)

    class Meta:
        verbose_name = _(u'order_item')
        verbose_name_plural = _(u'order_items')
        ordering = ('-create_date',)

    def __unicode__(self):
        return u'заказ №%s' % self.id

#    def get_order_status(self):
#        if self.order_carting == 'processed':
#            result = u'Обрабатывается'
#        elif self.order_carting == 'posted':
#            result = u'Отправлен'
#        elif self.order_carting == 'delivered':
#            result = u'Доставлен'
#        elif self.order_carting == 'cancelled':
#            result = u'Отменен'
#        else:
#            result = u''
#        return result

    def get_products(self):
        return self.orderproduct_set.select_related().all()

    def get_products_count(self):
        return self.get_products().count()

    def get_total(self):
        sum = 0
        for order_product in self.orderproduct_set.select_related().all():
            sum += order_product.get_total()
        return sum

    def get_str_total(self):
        total = self.get_total()
        value = u'%s' % total
        if isinstance(total,int):
            value = u'%s' % value[:len(value) - 3]
            count = 3
        else:
            count = 6

        if len(value) > count:
            ends = value[len(value) - count:]
            starts = value[:len(value) - count]

            return u'%s %s' % (starts, ends)
        else:
            return value

    def admin_summary(self):
        return '<span>%s</span>' % self.get_str_total()

    admin_summary.allow_tags = True
    admin_summary.short_description = 'Сумма'

    def fullname(self):
        return '<span>%s %s</span>' % (self.first_name, self.last_name)

    fullname.allow_tags = True
    fullname.short_description = 'Имя'

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'Заказ')
    count = models.PositiveIntegerField(default=1, verbose_name=u'Количество')
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    size = models.ForeignKey(Size, verbose_name=u'размер')

    def __unicode__(self):
        return u'на сумму %s руб.' % self.get_str_total()

    class Meta:
        verbose_name = _(u'product_item')
        verbose_name_plural = _(u'product_items')

    def get_total(self):
        total = self.product.price * self.count
        return total

    def get_str_total(self):
        total = self.get_total()
        value = u'%s' % total
        if total._isinteger():
            value = u'%s' % value[:len(value) - 3]
            count = 3
        else:
            count = 6

        if len(value) > count:
            ends = value[len(value) - count:]
            starts = value[:len(value) - count]

            return u'%s %s' % (starts, ends)
        else:
            return value

class EmsCity(models.Model):
    value = models.CharField(max_length=100, verbose_name=u'Код')
    name = models.CharField(max_length=100, verbose_name=u'Название')

    def __unicode__(self):
        return self.value

    class Meta:
        verbose_name = _(u'product_item')
        verbose_name_plural = _(u'product_items')


