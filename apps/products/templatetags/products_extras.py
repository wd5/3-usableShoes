# -*- coding: utf-8 -*-
from django import template
from django.db.models import Q
from apps.products.models import Target, Category
from apps.pages.models import Page
from apps.utils.utils import url_spliter

register = template.Library()

@register.inclusion_tag("products/block_catalog_menu.html")
def block_catalog_menu(url):
    current = url_spliter(url,3)

    menu = Target.objects.published()
    return {'menu': menu, 'current': current}

@register.inclusion_tag("products/block_catalog_submenu.html")
def block_catalog_submenu(type, url, object, categ):
#    try:
#        design_collection = Category.objects.get(pk=11)
#        dc_current =  url_spliter(url,3)
#    except Page.DoesNotExist:
#        dc_current = False
#        design_collection = False

    current = url_spliter(url,False)

    if type=='categ':
        sizes = object.sizes
        category = object
    else:
        sizes = False
        category = False

    if type=='product':
        product = object
        prod_cat = categ
    else:
        product = False
        prod_cat = False

    return {'sizes': sizes, 'current': current, 'prod_cat':prod_cat,
#            'dc_current': dc_current,
#            'dc':design_collection,
            'type':type, 'product':product, 'category':category }
