# -*- coding: utf-8 -*-
from django.conf.urls.defaults import url, patterns, include
from views import *


urlpatterns = patterns('',
    url(r'^search/$',search_view, name='products_search'),
    url(r'^product/(?P<pk>\d+)/$',product_view, name='products_detail'),

)
