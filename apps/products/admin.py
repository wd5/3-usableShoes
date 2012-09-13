# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms
from apps.utils.widgets import Redactor
from sorl.thumbnail.admin import AdminImageMixin
from mptt.admin import MPTTModelAdmin

from models import *

class TargetAdmin(admin.ModelAdmin):
    list_display = ('id','title','order','is_published',)
    list_display_links = ('id','title',)
    list_editable = ('order','is_published',)

admin.site.register(Target, TargetAdmin)

class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category

    class Media:
        js = (
            '/media/js/jquery.js',
            '/media/js/clientadmin.js',
            '/media/js/jquery.synctranslit.js',
            )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','title','slug','order','is_published',)
    list_display_links = ('id','title',)
    list_editable = ('slug','order','is_published',)
    list_filter = ('target',)
    #form = CategoryAdminForm

admin.site.register(Category, CategoryAdmin)

class SizeAdmin(admin.ModelAdmin):
    list_display = ('id','value',)
    list_display_links = ('id','value',)

admin.site.register(Size, SizeAdmin)

class ProductImageInline(AdminImageMixin, admin.TabularInline):
    model = ProductImage

#--Виджеты jquery Редактора
class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=Redactor(attrs={'cols': 110, 'rows': 20}), required=False)
    description.label=u'Описание'

    class Meta:
        model = Product

#--Виджеты jquery Редактора
class ProductAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id','title','art','price', 'order','is_published',)
    list_display_links = ('id','title','art',)
    list_editable = ('order','is_published',)
    list_filter = ('is_published','category','size',)
    search_fields = ('title', 'description', 'art','material',)
    filter_horizontal = ('size','related_products','category')
    inlines = [ProductImageInline]
    form = ProductAdminForm

admin.site.register(Product, ProductAdmin)

class ClientAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id','title','order','is_published',)
    list_display_links = ('id','title',)
    list_editable = ('order','is_published',)

admin.site.register(Client, ClientAdmin)

#class PhraseAdmin(admin.ModelAdmin):
#    list_display = ('id','example',)
#    list_display_links = ('id','example',)
#    search_fields = ('example',)
#
#admin.site.register(Phrase, PhraseAdmin)