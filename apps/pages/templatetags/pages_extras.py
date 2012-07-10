# -*- coding: utf-8 -*-
from apps.pages.models import Page
from apps.utils.utils import url_spliter
from django import template

register = template.Library()

@register.inclusion_tag("pages/block_page_summary.html")
def block_page_summary(alias):
    try:
        page = Page.objects.get(url=alias)
        return {'page': page}
    except Page.DoesNotExist:
        return {}

#def get_active_menu(url, site_menu):
#
#    request_path = url
#
#    for i, menu_item in enumerate(site_menu):
#        setattr(site_menu[i], 'is_active', False)
#        #if request_path.startswith(menu_item.path):
#            #site_menu[i].is_active = True
#
#
#    for i, menu_item in enumerate(site_menu):
#        setattr(site_menu[i], 'is_active', False)
#        if not menu_item.parent:
#            for menu_subitem in site_menu:
#                # highlight parent menu item
#                if menu_subitem.parent == menu_item and menu_subitem.is_active:
#                    site_menu[i].is_active = True
#        elif menu_item.is_active:
#            for menu_subitem in site_menu:
#                # remove redundant sibling highlight
#                if menu_subitem.parent \
#                     and menu_subitem.parent.path == menu_item.parent.path \
#                     and menu_subitem.path.startswith(menu_item.path) \
#                     and len(menu_subitem.path) > len(menu_item.path) \
#                     and menu_subitem.is_active:
#                        site_menu[i].is_active = False
#    return site_menu

@register.inclusion_tag("pages/block_menu.html")
def block_menu(url):
    current = url_spliter(url,1)
    menu = Page.objects.filter(parent=None, is_published=True, is_at_menu=True)
    #menu = get_active_menu(url, menu)
    return {'menu': menu, 'current': current}


@register.inclusion_tag("pages/block_second_menu.html")
def block_second_menu():
    menu = Page.objects.filter(parent=None, is_published=True, is_at_footer_menu=True)
    return {'menu': menu, }

@register.inclusion_tag("pages/block_top_h.html")
def block_top_h(title):
    return {'title': title, }

