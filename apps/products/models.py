# -*- coding: utf-8 -*-
import os, datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from apps.utils.managers import PublishedManager

from pytils.translit import translify
from django.core.urlresolvers import reverse

from sorl.thumbnail import ImageField
from mptt.models import MPTTModel, TreeForeignKey, TreeManager

from sorl.thumbnail import ImageField  as sorl_ImageField, get_thumbnail

from apps.utils.models import ImageCropMixin

class ImageField(sorl_ImageField, models.ImageField):
    pass

def file_path(instance, filename):
    return os.path.join('images','slider',  translify(filename).replace(' ', '_') )

class Target(models.Model):
    title = models.CharField(verbose_name=u'назначение', max_length=100)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_opt = models.BooleanField(verbose_name = u'Оптовая', default=False)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name =_(u'target')
        verbose_name_plural =_(u'targets')
        ordering = ['-order',]

    def get_categories(self):
        return self.category_set.published()

class Category(models.Model):
    target = models.ForeignKey(Target, verbose_name=u'назначение', blank=True, null=True)
    title = models.CharField(verbose_name=u'название', max_length=100)
    image = ImageField(verbose_name=u'Картинка', upload_to=file_path, blank=True, null=True,)
    description = models.TextField(verbose_name=u'', blank=True, null=True,)
    title_menu = models.CharField(verbose_name=u'название категории в меню', max_length=100)
    slug = models.SlugField(verbose_name=u'Алиас', help_text=u'уникальное имя на латинице',)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name =_(u'category')
        verbose_name_plural =_(u'categories')
        ordering = ['-order',]

    def get_absolute_url(self):
        return reverse('show_category',kwargs={'slug': '%s'%self.slug})

    def get_products(self):
        return self.product_set.published()

    def get_products_sizes(self):
        sizes = []
        products = self.get_products()
        for product in products:
            for size in product.get_sizes():
                sizes.append(size.value)
        sizes = list(set(sizes))
        sizes.sort()
        return sizes


def str_price(price):
    if not price:
        return u'0'
    value = u'%s' %price
    if price._isinteger():
        value = u'%s' %value[:len(value)-3]
        count = 3
    else:
        count = 6

    if len(value)>count:
        ends = value[len(value)-count:]
        starts = value[:len(value)-count]

        return u'%s %s' %(starts, ends)
    else:
        return value

class Size(models.Model):
    value = models.IntegerField(verbose_name=u'значение',)

    def __unicode__(self):
        return u'%s' % self.value

    class Meta:
        verbose_name =_(u'size')
        verbose_name_plural =_(u'sizes')
        ordering = ['-value',]


def file_path_Product(instance, filename):
    return os.path.join('images','products',  translify(filename).replace(' ', '_') )

s_choices = (
    (u'female',u'Женская'),
    (u'male',u'Мужская'),
    (u'child',u'Детская'),
)

trade_choices = (
    (u'hit',u'Хиты продаж'),
    (u'sale',u'Распродажа'),
    (u'new',u'Новые модели'),
)

class Product(models.Model):
    category = models.ManyToManyField(Category, verbose_name=u'Категория',)

    title = models.CharField(verbose_name=u'название', max_length=400)
    size = models.ManyToManyField(Size, verbose_name=u'размер')
    count = models.PositiveIntegerField(verbose_name=u'количество в коробке', null=True)
    art = models.CharField(verbose_name=u'артикул', max_length=50, blank=True)
    material = models.CharField(verbose_name=u'материал', max_length=150, blank=True)
    color = models.CharField(verbose_name=u'цвет', max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, verbose_name=u'описание')
    price = models.DecimalField(verbose_name=u'Цена', decimal_places=2, max_digits=10,)
    image = ImageField(verbose_name=u'изображение', upload_to=file_path_Product)
    s_type = models.CharField(max_length=20, verbose_name=u'Тип обуви', choices=s_choices,)
    trade_type = models.CharField(max_length=20, verbose_name=u'Тип предложения', choices=trade_choices, blank=True)

    related_products = models.ManyToManyField("self", verbose_name=u'Похожие товары', blank=True, null=True,)

    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        verbose_name =_(u'product_item')
        verbose_name_plural =_(u'product_items')
        ordering = ['-order',]

    def __unicode__(self):
        return u'%s. Артикул: %s' % (self.title,self.art)

    def get_absolute_url(self):
        for item in self.get_categories():
            #return reverse('show_product',kwargs={'pk': '%s'%self.id,'slug':'%s'%item.slug,'s_type':'%s'%self.s_type})
            return reverse('show_product',kwargs={'pk': '%s'%self.id,'slug':'%s'%item.slug})

    def get_short_url(self):
        return u'%s/'% (self.id)

    def get_str_price_for_box(self):
        price = self.price * self.count
        return str_price(price)

    def get_str_price(self):
        return str_price(self.price)

    def get_related_products(self):
        return self.related_products.published()

    def get_sizes(self):
        return self.size.all()

    def get_min(self):
        min = self.size.aggregate(min=models.Min('value'))
        return min['min']

    def get_max(self):
        max = self.size.aggregate(max=models.Max('value'))
        return max['max']

    def get_categories(self):
        return self.category.published()

    def get_photos(self):
        return self.productimage_set.all()

def file_path_Product(instance, filename):
     return os.path.join('images','products',  translify(filename).replace(' ', '_') )

class ProductImage(models.Model):
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    image = ImageField(verbose_name=u'Картинка', upload_to=file_path_Product)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)

    class Meta:
        ordering = ['-order',]
        verbose_name =_(u'product_photo')
        verbose_name_plural =_(u'product_photos')

    def __unicode__(self):
        return u'изображение товара %s' %self.product.title

def file_path_Client(instance, filename):
    return os.path.join('images','clients',  translify(filename).replace(' ', '_') )

class Client(models.Model):
    title = models.CharField(verbose_name=u'название', max_length=400)
    image = ImageField(verbose_name=u'Картинка', upload_to=file_path_Client, blank=True)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    description = models.TextField(verbose_name=u'описание',)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        verbose_name =_(u'client')
        verbose_name_plural =_(u'clients')
        ordering = ['-order',]

    def __unicode__(self):
        return self.title

#Класс фраз для поиска
#class Phrase(models.Model):
#    example = models.CharField(verbose_name=u'Пример фразы', max_length=100)
#
#    class Meta:
#        verbose_name =_(u'phrase')
#        verbose_name_plural =_(u'phrases')
#
#    def __unicode__(self):
#        return self.example
