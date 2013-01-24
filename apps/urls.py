# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from apps.products.views import show_catalog_by_type, show_category, show_product, clients_list, load_catalog, search_products
from apps.spam.views import add_subscribe, cancel_subscribe
from apps.users.views import show_cabinet, edt_profile_info, show_profile_form, registration_form
from apps.faq.views import review_list
from apps.users.views import items_loader


#url(r'^captcha/', include('captcha.urls')),

urlpatterns = patterns('',
    url(r'^$',show_catalog_by_type, {'type':'all'}, name='index', ),
    (r'^load_items/$',csrf_exempt(items_loader)),
    url(r'^catalog/$',show_catalog_by_type, {'type':'all'}, name='show_catalog', ),
    (r'^catalog/search/$',search_products,),
    url(r'^catalog/(?P<type>[^/]+)/$',show_catalog_by_type, name='show_catalog_by_type'),
    url(r'^catalog/category/(?P<slug>[^/]+)/$',show_category, {'s_type':'all'}, name='show_category' ),
    url(r'^catalog/category/(?P<slug>[^/]+)/$',show_category, name='show_category_by_type'),
    url(r'^catalog/category/(?P<slug>[^/]+)/(?P<pk>[^/]+)/$',show_product, name='show_product'),
    (r'^load_catalog/$',load_catalog),

    (r'^clients/$',clients_list),

    url(r'^faq/', include('apps.faq.urls')),
    url(r'^reviews/$',review_list, name='reviews_list'),

    (r'^add_subscribe_email/$', add_subscribe),
    (r'^cancel_subscribe/(?P<email>[^/]+)/$', cancel_subscribe),

    url(r'^cabinet/$',show_cabinet, name='show_cabinet'),
    (r'^cabinet/edit_info_form/$',show_profile_form),
    (r'^edt_profile_info/$',edt_profile_info),
    (r'^registration_form/$',registration_form),
    url(r'^password/reset/$',
        auth_views.password_reset,
            {'template_name': 'users/password_reset_form.html',},
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
            {'template_name': 'users/password_reset_confirm.html'},
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
            {'template_name': 'users/password_reset_complete.html'},
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
            {'template_name': 'users/password_reset_done.html'},
        name='auth_password_reset_done'),

    url(r'^cart/$','apps.orders.views.view_cart',name='cart'),
    (r'^add_product_to_cart/$','apps.orders.views.add_product_to_cart'),
    (r'^delete_product_from_cart/$','apps.orders.views.delete_product_from_cart'),
    (r'^restore_product_to_cart/$','apps.orders.views.restore_product_to_cart'),

    (r'^add_same_product_to_cart/$','apps.orders.views.add_same_product_to_cart'),
    (r'^show_modal_to_cart/$','apps.orders.views.show_modal_to_cart'),
    (r'^change_cart_product_count/$','apps.orders.views.change_cart_product_count'),
    (r'^show_order_form/$','apps.orders.views.show_order_form'),
    (r'^order_form_step2/$','apps.orders.views.show_finish_form'),

    (r'^ems_calculate/$','apps.orders.views.ems_calculate'),
    (r'^search_ems_city/$','apps.orders.views.search_ems_city'),
)



