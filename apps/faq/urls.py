# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from views import questions_list, review_list


urlpatterns = patterns('',

    url(r'^$',questions_list, name='questions_list'),
    url(r'^sendquestion/$','apps.faq.views.question_form'),
    url(r'^checkform/$','apps.faq.views.SaveQuestionForm'),

    url(r'^reviews/$',review_list, name='reviews_list'),
    url(r'^sendreview/$','apps.faq.views.review_form'),
    url(r'^checkreviewform/$','apps.faq.views.SaveReviewForm'),



)